# GUI implemented using: https://www.geeksforgeeks.org/gui-chat-application-using-tkinter-in-python/
import socket
from tkinter import *


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
    # constructor method
    def __init__(self, client):
        ###additional variables####
        self.client = client
        self.terminator = "#"
        self.chat_started = False
        self.fer_result = "None"
        ###########################
 
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
 
        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Login")
        self.login.resizable(width=False,
                             height=False)
        self.login.configure(width=400,
                             height=300)
        # create a Label
        self.pls = Label(self.login,
                         text="Please login to continue",
                         justify=CENTER,
                         font="Helvetica 14 bold")
 
        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        # create a Label
        self.labelName = Label(self.login,
                               text="Name: ",
                               font="Helvetica 12")
 
        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.2)
 
        # create a entry box for
        # tyoing the message
        self.entryName = Entry(self.login,
                               font="Helvetica 14")
 
        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.2)
 
        # set the focus of the cursor
        self.entryName.focus()
 
        # create a Continue Button
        # along with action
        self.go = Button(self.login,
                         text="CONTINUE",
                         font="Helvetica 14 bold",
                         command=lambda: self.beginChat(self.entryName.get()))
 
        self.go.place(relx=0.4,
                      rely=0.55)
        
        self.Window.after(10, self.getCurrentFER)
        self.Window.mainloop()
 
    def beginChat(self, name):
        self.login.destroy()
        self.layout(name)
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
            
        self.Window.after(10, self.getCurrentFER)  # reschedule event in 2 seconds
 
    
 
    # The main layout of the chat
    def layout(self, name):
 
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=470,
                              height=550,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="Starting Camera...",
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
 
        self.entryMsg = Entry(self.labelBottom,
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
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryMsg.get()))
 
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
 
    ###TODO: Create Query Augmentation Phrases Dict.
    def getQueryAugmentation(self):
        aug_dict = {'None':[],
                    'Neutral':[],
                    'Happy':["Reply as if I am really happy!"], 
                    'Sad':["Reply as if I am really sad!"],
                    'Surprise':["Reply as if I am really surprised!"],
                    'Fear':["Reply as if I am really scared!"],
                    'Disgust':["Reply as if I am really disgusted!"],
                    'Angry':["Reply as if I am really angry!"]}
                    
        return ""
 
    ##TODO: get LLM response to query. Add query Agumentation phrases as well
    def getLLMResponse(self):
        user_query = self.msg
        query_augmentation = self.getQueryAugmentation()
        
        LLM_response = "No LLM Implemented yet"
        
        self.reply = LLM_response
        
 
    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)
        
        self.getLLMResponse() ##FUNCTION NOT YET IMPLEMENTED!

        # insert messages to text box
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END,
                             self.name+": "+self.msg+"\n" + "Chatbot: " + self.reply + "\n")

        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
 

def main():
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
    

    
if __name__ == "__main__":
    main()
