#import tkinter
#Traceback (most recent call last):
#  File "<pyshell#11>", line 1, in <module>
#    import tkinter
#ImportError: No module named tkinter

import sys, Tkinter
sys.modules['tkinter'] = Tkinter # put the module where python looks first for modules
#import tkinter # now works!

from tkinter import Tk, Text, BOTH, W, N, E, S, Frame, Button, Label, StringVar, Message,DISABLED, NORMAL, Scrollbar, LEFT, RIGHT, WORD, Entry,END

import time
import Queue
import threading
import socket
import re
import encodings.idna
import sys



class LaunchApp:
    """Startup the program and open GUI"""

    def __init__(self,socket, name, friend_name):
        self.chat_sock=socket
        self.name=name
        self.friend=friend_name

        #Launch thread to do I/O on the socket
        self.running=1
        self.sockthread=threading.Thread(target=self.listen)
        self.sockthread.start()
        
        self.inputThread = threading.Thread(target=self.newmsg())
        self.inputThread.start()
        # this is buggy. I dont think inputThread is returning properly so ctrl c causes process to hang
        # after ctrl c-ing, run ps -C python and manually kill process
        while True:
            self.inputThread.join(500)
            if not self.inputThread.isAlive():
                print "input thread is dead"
                sys.exit(1)
                break

    def listen(self):
        """
        Handle socket I/O stuff here
        """
        inc_message=""
        while self.running:
            inc_message=self.chat_sock.recv(16384)
            if inc_message!="":
                pretty_msg=self.friend+": "+inc_message.decode()
                print pretty_msg
                print (">>"),
                #that previous print has no newline so stdout doesnt flush, do it manually
                sys.stdout.flush()
                inc_message=""

    def newmsg(self):
        while self.running:
            message = raw_input(">>")
            
            #encode message for transfer into socket
            msg_to_send=message.encode()
        
            #send message into socket
            self.chat_sock.send(msg_to_send)

#Options for startup
def options():
        print("Would you like to:\n 1. Wait for a connection\
        \n 2. Start a connection\n 3. Quit\n")
        choice=int(raw_input("Input Number "))
        if [1,2,3].count(choice)==0:
             print("\nInvalid entry, please enter an integer 1, 2, or 3\n")
             time.sleep(.5)
             choice=options()
        return choice





def main():
    sendport=12345
    receiveport=12345
    host=socket.gethostname()

    name=str(raw_input("What is your name? "))
    print("\nHello "+name+"!!\n")
    time.sleep(.5)

    choice=options()

    #If they selected to wait
    if choice==1:
        serverTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverTCP.bind((host,receiveport))        
        serverTCP.listen(5)
        chat_sock,addr=serverTCP.accept()
        friend=chat_sock.recv(16384).decode() #first msg received must be friend's name
        
    #If they selected to initiate
    elif choice==2:
        chat_sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        friend=raw_input("Who do you want to connect to? ")
        friend_address=raw_input("What is their IP address? ")                  
        chat_sock.connect((friend_address,sendport))
        chat_sock.send(name.encode())

    #If they selected to quit    
    elif choice==3:
        print("\nBye!!!\n")
        time.sleep(2)
        sys.exit

    runprogram=LaunchApp(chat_sock,name,friend)


if __name__ == '__main__':
    main()    




