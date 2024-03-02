# GUI implemented using: https://www.geeksforgeeks.org/gui-chat-application-using-tkinter-in-python/
import socket
from tkinter import *
from chatHandler import ChatHandler
import os
import openai


#############################################
############# IMPORTANT #####################
#############################################
# This will look on your system for an environment variable
# to use as a key.
#   Set one. You may have to restart your IDE afterward.
#        Please use this command in a cmd prompt:
# setx OPENAI_API_KEY “<yourkey>”

try:
    #openai.api_key = os.environ["OPENAI_API_KEY"]
    key = os.environ["OPENAI_API_KEY"]
except Exception as e:
    print("NO KEY ENVIRONMENT VARIABLE FOUND, PLEASE INPUT AT LOGIN.")
    print(e)


# run videostream_loop.py in a cmd window before you run this
useServer = False # set to false to run GUI only

"""
Version 1.0 of Gui application.

Widget to Display current detected FER result: Complete
Text entry & display: Complete

QUery Augmentation dict: Skeleton Function Created: getQueryAugmentation()
LLM Response Function: Skeleton Function Created: getLLMResponse()

Microphone button/speech to text entry: Not Yet Implemented
"""



########################################
################ GUI ###################
########################################

# GUI class for the chat
class GUI:
    # constructor method with video stream client
    # set client  to None for gui only
    def __init__(self, client):
        ###additional variables####
        if client == None:
            self.usingServer = False
        else:
            self.usingServer = True
        self.client = client
        self.terminator = "#"
        self.chat_started = False
        self.fer_result = "None"
        ####### more variables ######
        self.chatHandler = ChatHandler()
        self.name = '' # api-key variable... so poorly named... I'm sorry.... :(
        self.userName = ''
        self.augMsg = '' # augmented message (augmentation + original message
        self.reply = '' # the response from chatbot
        self.msg = '' # the original message typed in
        self.showAugmentation = True # output the emotional augmentation being used
        self.aug_dict = {'None':[""],
            'Neutral':["(Reply as if I have a neutral facial expression)"],
            'Happy':["(Reply as if I am really happy)"], 
            'Sad':["(Reply as if I am really sad)"],
            'Surprise':["(Reply as if I am really surprised)"],
            'Fear':["(Reply as if I am really scared)"],
            'Disgust':["(Reply as if I am really disgusted)"],
            'Angry':["(Reply as if I am really angry)"]}

        self.commandPrefix = "%%%" # prefix to enter a command to the system (see sendButton())
        # dictionary of available commanable variables and their values
        self.commandList = ['self.showAugmentation']
        
        ###################################
        #   BEGIN WINDOW CONSTRUCTION
        ###################################
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
 
        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("api-key and name")
        self.login.resizable(width=True,
                             height=True)
        self.login.configure(width=800,
                             height=300)
        # create a Label for api-key
        self.pls = Label(self.login,
                         text="Please enter an api-key (or leave it blank to skip).",
                         justify=CENTER,
                         font="Helvetica 14 bold")
 
        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        # entry box for api-key (or return to skip)
        self.entryName = Entry(self.login,
                               font="Helvetica 14")
 
        self.entryName.place(relwidth=0.6,
                             relheight=0.1,
                             relx=0.1,
                             rely=0.3)
 
        # create a Label for user name
        self.labelName = Label(self.login,
                               text="Enter a name you'd like to use (optional). ",
                               justify=CENTER,
                               font="Helvetica 12")
 
        self.labelName.place(relheight=0.6,
                             relx=0.1,
                             rely=0.2)

        # create a entry box for user name 
        self.entryUserName = Entry(self.login,
                               font="Helvetica 14")
 
        self.entryUserName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.6)
 
        # set the focus of the cursor on the api-key box (also responds to return)
        self.entryName.focus()
 
        # create a Continue Button
        # along with action
        # make this button respond to 'return' as well
        self.login.bind("<Return>", lambda e: self.beginChat(self.entryName.get(), userName = self.entryUserName.get()))

        self.go = Button(self.login,
                         text="CONTINUE",
                         font="Helvetica 14 bold",
                         command=lambda: self.beginChat(self.entryName.get(), userName = self.entryUserName.get()))
        self.go.pack() # activate the return binding
        
        self.go.place(relx=0.4,
                      rely=0.8)

        if self.client != None:
            self.Window.after(10, self.getCurrentFER)

        self.Window.mainloop()    
 
    # The main layout of the chat
    def layout(self, name):
 
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=True,
                              height=True)
        self.Window.configure(width=470,
                              height=550,
                              bg="#17202A")
        if self.client != None:
            self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="Starting Camera...",
                               font="Helvetica 13 bold",
                               pady=5)
        else:
            self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="No Server Detected... no emotions will be added.",
                               font="Helvetica 13 bold",
                               pady=5)
        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")
 
        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)
 
        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)
 
        self.textCons.place(relheight=0.745,
                            relwidth=1,
                            rely=0.08)
 
        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)
 
        self.labelBottom.place(relwidth=1,
                               rely=0.825)
 
        self.entryMsg = Text(self.labelBottom,
                              bg="#2C3E50",
                              fg="#EAECEE",
                              font="Helvetica 13")
 
        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth=0.74,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)
 
        self.entryMsg.focus()
        
        # create a Send Button
        # make it respond to 'ctrl+return' too.
        self.Window.bind("<Shift-Return>", lambda e: self.sendButton(self.entryMsg.get("1.0","end")))
        
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryMsg.get("1.0","end")))
        self.buttonMsg.pack() # activate the return binding
        self.buttonMsg.place(relx=0.77,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.22)
 
        self.textCons.config(cursor="arrow")
 
        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)
 
        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)
 
        scrollbar.config(command=self.textCons.yview)
 
        self.textCons.config(state=DISABLED)

    def beginChat(self, name, userName = ':'): #############################
        self.login.destroy()
        self.layout(name) # api-key... poorly named variable :(
        self.userName = userName
        try:
            self.chatHandler.initializeAPI(api_key = key)
        except:
            self.chatHandler.initializeAPI(api_key = name)
        self.chat_started = True
 
    def getCurrentFER(self, delay = 10):
        if self.chat_started:
            try:
                raw_message = str(self.client.recv(1024).decode('utf-8'))
                fer_list = [result for result in raw_message.split(self.terminator) if result != '']
                self.fer_result = fer_list[-1]
                self.labelHead.config(text="Detected Emotion: " + str(self.fer_result))
            except:
                print("no message from server")
                self.labelHead.config(text="No Server Detected: " + str(self.fer_result))
        self.Window.after(10, self.getCurrentFER)  # reschedule event in 2 seconds
 
    def getQueryAugmentation(self, index = 0):
        if self.fer_result in self.aug_dict:
            self.queryAug = self.aug_dict[self.fer_result][index]
        else:
            self.queryAug = None

        return self.queryAug
 
    ##TODO: get LLM response to query. Add query Agumentation phrases as well
    def getLLMResponse(self):
        user_query = self.msg
        query_augmentation = self.getQueryAugmentation()

        try:
            self.chatHandler.defineMessage(message=user_query)
            self.chatHandler.sendMessage()
            LLM_response = self.chatHandler.returnReply()
        except Exception as e:
            print(e)
            LLM_response = "Problem with LLM handler: "
            
        self.reply = LLM_response
        return (self.reply)

    def composeAugMsg(self):
        self.getQueryAugmentation()
        self.augMsg = self.queryAug + " " + self.msg
        return self.augMsg
    def setAugDisplay(self, value): # show or hide augmentation from user
        self.showAugmentation = value
        
    # function to basically start the thread for sending messages
    def sendButton(self, msg): # also gets called with binding (e.g., <Shift-Return>)
        self.textCons.config(state=DISABLED)
        self.msg = msg

        if self.commandPrefix not in self.msg:
            # get emotion, augmentation, compose with msg, and get response
            self.composeAugMsg()
            self.entryMsg.delete('1.0', 'end') # clean up
            self.getLLMResponse()

            # insert messages to text box
            self.textCons.config(state=NORMAL)
            if self.showAugmentation:
                self.textCons.insert(END,
                                     "\n"+self.userName+": "+self.augMsg + "Chatbot: " + self.reply + "\n")
            else:
                self.textCons.insert(END,
                                     "\n"+self.userName+": "+self.msg + "Chatbot: " + self.reply + "\n")
                

            self.textCons.config(state=DISABLED)
            self.textCons.see(END)

        else: # user is changing some variables with the commandPrefix     
            self.entryMsg.delete('1.0', 'end') # clean up
            self.textCons.config(state=NORMAL)

        try:
            command = self.msg.split()
            self.textCons.insert(END, "\n"+self.commandPrefix+"  SYSTEM COMMAND  "+self.commandPrefix+"\n")
            if command[1] in self.commandList:
                exec(f'{command[1]}={command[2]}')
                self.textCons.insert(END, command[1] +"  =  "+ command[2]+"\n")
                output=f'{command[1]} now set to: '
                output=output+str(eval(command[1]))
                                    
                self.textCons.insert(END, output+'\n')
            elif command[1] == 'print':
                self.textCons.insert(END, command[1] +' '+ command[2] + "\n")
                self.textCons.insert(END, f'{command[2]} equal to: ' + str(eval(command[2])))

        except:
            self.textCons.insert(END, self.commandPrefix+"  COMMAND NOT UNDERSTOOD  "+self.commandPrefix+"\n")
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            
def main(useVideoStream = True):
    if useVideoStream == True:
        port = 400
        host = socket.gethostname()
        
        connection_attempts = 5000
        connect_success = False
        for i in range(connection_attempts):
            if not connect_success:
                try:
                    client = socket.socket(socket.AF_INET,
                                       socket.SOCK_STREAM)
                    client.connect((host, port))
                    
                    chat_app = GUI(client)
                    connect_success = True
                    
                except:
                    if i%(connection_attempts//10)==0:
                        print("Failed to connect, retrying")
                    continue
        
        if not connect_success: 
            print("Failed to connect to Videostream server! Please ensure it is running first.")
        else:
            print("Thanks for using this app.")

    # run GUI only for dev purposes
    else:
        chat_app = GUI(client = None)

if __name__ == "__main__":
    if useServer == True:
        main()
    # use the following to run the GUI only
    else:
        main(False)
