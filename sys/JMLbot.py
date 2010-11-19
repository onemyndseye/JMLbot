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

#from net.sf.jml import MsnFileTransfer
from net.sf.jml import MsnProtocol
#from net.sf.jml.message import MsnControlMessage
from org.apache.http.params import HttpParams



class MSNEventHandler(MsnAdapter):
    #overridden call back functions
    def instantMessageReceived(self, switchboard,message,contact):
        receivedText = message.getContent()
        #set the switchboard, so that we can send messages
        self.switchboard = switchboard
 
        ext_handler = Config.get('System','event_handler') + " "
        contact_id = str(contact.getEmail()) + " "
        contact_name = str(contact.getFriendlyName()) + " "

        cmdline = ext_handler + contact_id + receivedText
        output = os.popen(cmdline).read()

        # Send typing notify        
        typingMessage = MsnControlMessage()
        typingMessage.setTypingUser(switchboard.getMessenger().getOwner().getDisplayName());
        self.sendMessage(typingMessage)
        time.sleep(2)

        #send the msg to the buddy        
        msnMessage = MsnInstantMessage()
        msnMessage.setContent(output)
        self.sendMessage(msnMessage)
    

    def contactAddedMe(self,messenger,contact):
        messenger.addFriend(contact.getEmail(),contact.getFriendlyName())
        
     #non overridden functions
    def sendMessage(self,message):
        self.switchboard.sendMessage(message)
        
class MSNMessenger:
    def initMessenger(self,messenger):
        print "Initializing...."
        listener = MSNEventHandler()
        messenger.addMessageListener(listener)
        messenger.addFileTransferListener(listener)
        messenger.addContactListListener(listener)        
    
    def PostLoginSetup(self,messenger):     
        # Lets do some client setup before moving on
        delay = Config.get('System','login_delay')
        time.sleep(int(delay))
        # Set screen name
        bot_screenname      = Config.get('Details','screenname') 
        messenger.getOwner().setDisplayName(bot_screenname)
        # Set avatar
        bot_avatar = Config.get('Details','avatar')
        displayPicture = MsnObject.getInstance(messenger.getOwner().getEmail().getEmailAddress(), bot_avatar) 
        messenger.getOwner().setInitDisplayPicture(displayPicture)
        # Set personal messenage
        statusmsg = Config.get('Details','status_message')
        messenger.getOwner().setPersonalMessage(statusmsg)
        # Set Status
        messenger.getOwner().setInitStatus(MsnUserStatus.ONLINE)
 		
    def connect(self,email,password):
        messenger = MsnMessengerFactory.createMsnMessenger(email,password)
        self.initMessenger(messenger)     
        print "   Logging in and setting screenname .."
        try:
           messenger.login()
        except:
           print "There was an error with login. Aborting.."
           sys.exit(100)
        MSNMessenger.PostLoginSetup(self,messenger)

           
class MSNConnector:
    def connect(self,username,password):
        messenger = MSNMessenger()
        messenger.connect(username,password)        


def usage():
    output = "Usage: \n"
    output = output + "-c/--config <file>  :::   Specify JMLbot config file \n"
    output = output + "-h/--help           :::   This message \n"
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
    print "   Login complete. Listening for events.."    

def main(argv):
    global config_file
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
        sleep(10)



if __name__ == "__main__":
    main(sys.argv[1:])

