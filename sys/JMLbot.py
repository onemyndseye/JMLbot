#!/usr/bin/env jython

### JMLbot is a MSN chatbot framework written in jython that makes use of 
### the java messenger library (http://jml.blathersource.org/). Based on the
### orignal work by Nathan Stehr (nstehr@gmail.com). 

__author__        = "J. Whittington (onemyndseye@yahoo.com)"
__version__       = "$Revision: 1.0 $"
__date__          = "$Date: 2010/011/14 $"
__license__       = "GPL2"


#from time import sleep
import sys
import os
import time
from time import sleep
import urllib
import getopt
import ConfigParser
import random
import linecache
import threading

#setup the path and add JML
current_path= os.getcwd()
sys.path.append(os.path.join(current_path,'jml-1.05b-full_http.jar'))
from net.sf.jml import MsnMessenger
from net.sf.jml import MsnUserStatus
from net.sf.jml.impl import MsnMessengerFactory
from net.sf.jml import MsnSwitchboard
from net.sf.jml.event import MsnAdapter
from net.sf.jml.message import MsnControlMessage
from net.sf.jml.message import MsnDatacastMessage
from net.sf.jml.message import MsnInstantMessage
from net.sf.jml import MsnContact
from net.sf.jml import Email
from net.sf.jml import MsnObject
from net.sf.jml import MsnProtocol
from org.apache.http.params import HttpParams


class MSNEventHandler(MsnAdapter):
    #overridden call back functions
    def instantMessageReceived(self, switchboard,message,contact):
        receivedText = message.getContent()
        #set the switchboard, so that we can send messages
        self.switchboard = switchboard
 
        if Config.get('System', 'auto_idle_events') == "yes":
          setIdleTimer.stop()
        ext_handler = Config.get('System','event_handler') + " "
        contact_id = str(contact.getEmail()) + " "
        contact_name = str(contact.getFriendlyName()) + " "

        if Config.get('System','send_typing') == "yes":
          # Send typing notify        
          typingMessage = MsnControlMessage()
          typingMessage.setTypingUser(switchboard.getMessenger().getOwner().getDisplayName());
          self.sendMessage(typingMessage)
          time.sleep(2)

        cmdline = ext_handler + contact_id + "'" + receivedText + "'"
        output = os.popen(cmdline).read()

        #send the msg to the buddy        
        msnMessage = MsnInstantMessage()
        msnMessage.setContent(output)
        self.sendMessage(msnMessage)
        if Config.get('System', 'auto_idle_events') == "yes":
          setIdleTimer.start()

    def contactAddedMe(self,messenger,contact):
        messenger.addFriend(contact.getEmail(),contact.getFriendlyName())
        
    #non overridden functions
    def sendMessage(self,message):
        self.switchboard.sendMessage(message)



class msnWatchDog(threading.Thread):
    def __init__ (self,messenger):
       self.messenger = messenger
       self._stopevent = threading.Event()
       threading.Thread.__init__ (self,name="msnWatchdog")

    def run(self):
       while 1:
           if str(self.messenger.getConnection()) == "None":
             print "\n My connection died. Will attempt to restart ..."
             print "     Closing active threads ..."
             setIdleTimer.stop()
             setStatusTimer.stop()
             print "     Restarting ..."
             start()
             threading.Thread.__init__(self)
             sys.exit()
           else:
             sleep(10)


class RandomStatus(threading.Thread):
    def __init__ (self, messenger,Config):
       self.messenger = messenger
       self.Config = Config
       self._stopevent = threading.Event()
       threading.Thread.__init__ (self)
     
    def run(self):
       status_sleep = self.Config.get('Details','status_time')
       status_file = self.Config.get('Details','status_file')
       status_num_lines = sum(1 for line in open(status_file))
       self._stopevent.clear()
       statusmsg = linecache.getline(status_file, random.randint(1,status_num_lines))
       self.messenger.getOwner().setPersonalMessage(statusmsg)
       count = 0
       while not self._stopevent.isSet():
           count += 1
           if count == int(status_sleep):
             statusmsg = linecache.getline(status_file, random.randint(1,status_num_lines))
             self.messenger.getOwner().setPersonalMessage(statusmsg)
             # Reset the counter
             count = 0
           time.sleep(1)      
       threading.Thread.__init__(self)

    def stop(self):
        self._stopevent.set()
        threading.Thread.join(self, timeout=0.1)
        self.join()        


class IdleStatus(threading.Thread):
    def __init__ (self, messenger,Config,BotStatus):
       self.messenger = messenger
       self.Config = Config
       self.BotStatus = BotStatus
       self._stopevent = threading.Event()
       threading.Thread.__init__ (self,name="idleCounter")
     
    def run(self):
       idle_time = self.Config.get('System','idle_time')
       away_time = self.Config.get('System','away_time')
       self._stopevent.clear()
       count = 0
       while not self._stopevent.isSet():
           count += 1
           if count == int(idle_time):
              self.messenger.getOwner().setStatus(MsnUserStatus.IDLE)
           elif count == int(away_time):
              self.messenger.getOwner().setStatus(MsnUserStatus.AWAY)
           time.sleep(1)       
       threading.Thread.__init__(self)

    def stop(self):
        self.messenger.getOwner().setStatus(self.BotStatus)
        self._stopevent.set()
        threading.Thread.join(self, timeout=0.1)
        self.join()        

class MSNMessenger:
    def initMessenger(self,messenger):
        print "Initializing...."
        listener = MSNEventHandler()
        messenger.addMessageListener(listener)
        messenger.addContactListListener(listener)        

    
    def PostLoginSetup(self,messenger):     
        # Hide until we are ready to take events
        messenger.getOwner().setInitStatus(MsnUserStatus.HIDE)
        print "   Setting up bot indenity ..."
        # Lets do some client setup before moving on
        delay = Config.get('System','login_delay')
        print "      Waiting " + delay + "secs for connection to settle ..."
        time.sleep(int(delay))
        # Set screen name
        bot_screenname      = Config.get('Details','screenname') 
        print "      Setting screen name to " + bot_screenname + " ..."
        messenger.getOwner().setDisplayName(bot_screenname)
        # Set avatar
        bot_avatar = Config.get('Details','avatar')
        print "      Setting avatar using " + bot_avatar + " ..."
        displayPicture = MsnObject.getInstance(messenger.getOwner().getEmail().getEmailAddress(), bot_avatar) 
        messenger.getOwner().setInitDisplayPicture(displayPicture)
        # Set personal message
        if Config.get('Details','random_status') == "yes":
           print "      Setting random status message ..."
           global setStatusTimer
           setStatusTimer = RandomStatus(messenger,Config)
           setStatusTimer.start()
        else:
           print "      Setting status message ..."
           statusmsg = Config.get('Details','status_message')
           messenger.getOwner().setPersonalMessage(statusmsg)
        # Set Status
        initStatus = Config.get('Details', 'status')
        print "      Setting status to " + initStatus + " ..."
        if initStatus == "away":
           BotStatus = MsnUserStatus.AWAY
        elif initStatus == "busy":
           BotStatus = MsnUserStatus.BUSY
        elif initStatus == "hide":
           BotStatus = MsnUserStatus.HIDE
        elif initStatus == "brb":
           BotStatus = MsnUserStatus.BE_RIGHT_BACK
        elif initStatus == "phone":
           BotStatus = MsnUserStatus.ON_THE_PHONE
        elif initStatus == "lunch":
           BotStatus = MsnUserStatus.OUT_TO_LUNCH
        else:
           # Default to online
           BotStatus = MsnUserStatus.ONLINE        
        messenger.getOwner().setStatus(BotStatus)
        if Config.get('System', 'auto_idle_events') == "yes":
          global setIdleTimer
          setIdleTimer = IdleStatus(messenger,Config,BotStatus)
          setIdleTimer.start()
          msnWatchDog(messenger).start()        
        
    def connect(self,email,password):
        messenger = MsnMessengerFactory.createMsnMessenger(email,password)
        self.initMessenger(messenger)     
        print "   Connecting ..."
        try:
           messenger.login()
        except:
           print "   Login failed. Aborting ..."
           sys.exit(100)
        MSNMessenger.PostLoginSetup(self,messenger)

           
class MSNConnector:
    def connect(self,username,password):
        messenger = MSNMessenger()
        messenger.connect(username,password)        


def usage():
    output = "Usage: \n"
    output = output + "--config <file>    :::   Specify JMLbot config file \n"
    output = output + "-h/--help          :::   This message \n"
    output = output + "\n"
    print output                     


def LoadConfig(config_file):
    if os.path.exists(config_file):
       load_msg = "Using config file: " + config_file
       print load_msg 
       global Config
       Config = ConfigParser.ConfigParser()
       Config.read(config_file)
    else:
       print "The specified config file does not exist!"
       sys.exit(1)

def start():
    connector = MSNConnector()
    bot_username        = Config.get('Account','username')
    bot_password        = Config.get('Account','password') 
    connector.connect(bot_username,bot_password)
    print "Initializing complete.  Listening for events ..."    


def main(argv):
    config_file=""
    try:                                
        opts, args = getopt.getopt(argv, "h", ["help", "config="])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)                     
    for opt, arg in opts:                
        if opt in ("-h", "--help"):      
            usage()                     
            sys.exit()                  
        elif opt in ("--config"): 
            config_file = arg               
        
    if config_file:
        LoadConfig(config_file)
    else:
        print "Please give a config file to load. see --help\n"
        sys.exit(1)

    start()
    while 1:
          time.sleep(10)
     
if __name__ == "__main__":
    main(sys.argv[1:])

