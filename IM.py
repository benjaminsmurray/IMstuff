
from tkinter import Tk, Text, BOTH, W, N, E, S, Frame, Button, Label, StringVar, Message,DISABLED, NORMAL, Scrollbar, LEFT, RIGHT, WORD, Entry,END
import time
import queue
import threading
import socket
import re
import encodings.idna
import sys



class GuiBox(Frame):
  
    def __init__(self, parent, queue, socket, name):
        self.queue=queue
        self.chat_sock=socket
        self.name=name
        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.initUI()
        
    def initUI(self):
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
     
        #Initial Value for Text Box
        time_start=time.strftime("%d %b %Y %I:%M:%S",time.localtime())
        first_txt="Conversation Started: "+time_start+"\n"
        
        #Setting up ScrollBar
        scroll=Scrollbar(self)
        scroll.grid(row=0,column=1,sticky=N+S)
        
        #Setting up chatbox
        self.chatbox = Text(self, bg="white", width=65, height=30,
                   yscrollcommand=scroll.set, wrap=WORD)

        self.chatbox.insert("insert",first_txt)
        self.chatbox.grid(row=0,column=0,sticky=N+E+W)
        self.chatbox.config(state=DISABLED)

        #Bind scrollbar to the chatbox
        scroll.config(command=self.chatbox.yview)
        #Create Composition box
        self.send=Text(self, width=68, height=3, wrap=WORD)
        self.send.grid(row=1,column=0, columnspan=2,pady=15)
        self.send.bind('<KeyRelease-Return>', self.__sendmsg)
        
        self.pack()           

    def __sendmsg(self, event):
        message=self.send.get("1.0",END)
        self.newmsg(message)
        self.send.delete("1.0",END)

        

    def newmsg(self, message):

        #format the message to print in chatbox
        pretty_msg=self.name+": "+message

        #encode message for transfer into socket
        msg_to_send=message.encode()
        
        #send message into socket
        self.chat_sock.send(msg_to_send)

        #print message in own chatbox
        
        self.chatbox.config(state=NORMAL)
        self.chatbox.insert(END,pretty_msg)
        self.chatbox.config(state=DISABLED)
        
           
    def getIncoming(self):
        """Handle messages currently in the queue, if any"""
        while self.queue.qsize():
            try:
                msg=self.queue.get(0)
                self.chatbox.config(state=NORMAL)
                self.chatbox.insert(END,msg)
                self.chatbox.config(state=DISABLED)
            except queue.Empty:
                pass
            
class LaunchApp:
    """Startup the program and open GUI"""

    def __init__(self,root, socket, name, friend_name):
        self.tkinterloop=root
        self.chat_sock=socket
        self.name=name
        self.friend=friend_name

        #Create queue
        self.queue=queue.Queue()

        #Create GUI Object
        self.gui=GuiBox(self.tkinterloop, self.queue, self.chat_sock, self.name)

        #Launch thread to do I/O on the socket
        self.running=1
        self.sockthread=threading.Thread(target=self.listen)
        self.sockthread.start()

        self.check_queue()

    def check_queue(self):
        """Check every 200 ms if there is something new in queue."""

        self.gui.getIncoming()
        if not self.running:
            #Force exit
            import sys
            sys.exit(1)
        self.tkinterloop.after(200,self.check_queue)
        

    def listen(self):
        """
        Handle socket I/O stuff here
        """
        inc_message=""
        while self.running:
            inc_message=self.chat_sock.recv(16384)
            if inc_message!="":
                pretty_msg=self.friend+": "+inc_message.decode()
                self.queue.put(pretty_msg)
                inc_message=""

    def endApplication(self):
        self.running=0


        

#Options for startup
def options():
        print("Would you like to:\n 1. Wait for a connection\
        \n 2. Start a connection\n 3. Quit\n")
        choice=int(input("Input Number "))
        if [1,2,3].count(choice)==0:
             print("\nInvalid entry, please enter an integer 1, 2, or 3\n")
             time.sleep(.5)
             choice=options()
        return choice





def main():


    sendport=12345
    receiveport=12345
    host=socket.gethostname()

    name=input("What is your name? ")
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
        friend=input("Who do you want to connect to? ")
        friend_address=input("What is their IP address? ")                  
        chat_sock.connect((friend_address,sendport))
        chat_sock.send(name.encode())

    #If they selected to quit    
    elif choice==3:
        print("\nBye!!!\n")
        time.sleep(2)
        sys.exit

    
    root = Tk()
    root.title("Windows")
    root.geometry("700x600+50+50")

    runprogram=LaunchApp(root,chat_sock,name,friend)
    root.mainloop()  


if __name__ == '__main__':
    main()    




