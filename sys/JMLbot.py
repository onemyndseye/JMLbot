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
sys.path.append(os.path.join(current_path,'jml-1.0b3-full.jar'))
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
from net.sf.jml import MsnFileTransfer



class MSNEventHandler(MsnAdapter):
    #overridden call back functions
    def instantMessageReceived(self, switchboard,message,contact):
        receivedText = message.getContent()
        #set the switchboard, so that we can send messages
        self.switchboard = switchboard

        ext_handler = Config.get('main','event_handler') + " "
        contact_id = str(contact.getEmail()) + " "
        contact_name = str(contact.getFriendlyName()) + " "

        cmdline = ext_handler + contact_id + receivedText
        output = os.popen(cmdline).read()

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
        
		
    def connect(self,email,password):
        messenger = MsnMessengerFactory.createMsnMessenger(email,password)
        messenger.getOwner().setInitStatus(MsnUserStatus.ONLINE)
        self.initMessenger(messenger)     
        print "   Logging in and setting screenname .."
        messenger.login()
        time.sleep( 3 )
        bot_screenname      = Config.get('main','screenname') 
        messenger.getOwner().setDisplayName(bot_screenname)


        
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
    bot_username        = Config.get('main','username')
    bot_password        = Config.get('main','password') 
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

