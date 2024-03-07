# GUI implemented using: https://www.geeksforgeeks.org/gui-chat-application-using-tkinter-in-python/
import os
import time
import socket
from tkinter import *
import tkinter.messagebox
import openai
from chatHandler import ChatHandler
from DoSpeech import DoSpeech
from PIL import Image, ImageTk

#############################################
############# IMPORTANT #####################
#############################################
# This will look on your system for an environment variable
# to use as a key.
#   Set one. You may have to restart your IDE afterward.
#        Please use this command in a cmd prompt:
#
#           setx OPENAI_API_KEY “<yourkey>”
#
# Alternatively, if you enter a key in at the login screen,
# I will try to set it as a environment variable on your system
# for you (and future logins, you can just press return to skip)

try:
    #openai.api_key = os.environ["OPENAI_API_KEY"]
    #raise Exception("testing api-key finding system...")
    key = os.environ["OPENAI_API_KEY"]
except Exception as e:
    print("NO KEY ENVIRONMENT VARIABLE FOUND, PLEASE INPUT AT LOGIN.")
    print(e)
    errorKeyWin = Tk()
    errorKeyWin.wm_withdraw()
    tkinter.messagebox.showinfo(title="No API KEY found...", \
                                message='''No api-key for the chat system was found in your systems' environmental variables.\n\n
Please enter a valid api-key at the login window, or the chat system will not work.\n\n
The api-key entered will be saved on your system so next time you will not need to do this.\n\n \
                                        Thankyou.\n''')
    errorKeyWin.destroy()


# run videostream_loop.py in a cmd window before you run this
useServer = False # set to false to run GUI only

# This will attempt to run the server for you in a (new) cmd window... please wait.
try:
    pathToVideoStreamLoop = 'start python ./videostream_loop.py' 
    if useServer:
        print("starting server...")
        # run videostream_loop.py
        import subprocess
        import sys
        #serverProcess = subprocess.Popen(pathToVideoStreamLoop, stdout=subprocess.PIPE, shell=True) 
        subprocess.Popen(pathToVideoStreamLoop, shell=True) 
        print("waiting for server to start...")
        time.sleep(10)
        print("done waiting...")
except:
    print("problem starting server... aborting server.")
    useServer = False

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
    def setAPIkeyAsEnvVar(self,key):
        try:
            os.environ["OPENAI_API_KEY"] = key
        except:
            print ("problem setting key as environmental variable")
            print("you will need to re-enter your key next time")

    # constructor method with video stream client
    # set client  to None for gui only
    def __init__(self, client):
        ###additional variables####
        if client == None:
            self.usingServer = False
        else:
            self.usingServer = True
            #self.serverProcess = p
        self.client = client
        self.terminator = "#"
        self.chat_started = False
        self.fer_result = "None"
        self.fer_image = './startImage.jpg' # image to display for a given fer_result
        self.startImage = './startImage.jpg' # image to display for a given fer_result
        self.userStartedTyping = False
        self.timeStartTyping = 0.0
        self.timeStopTyping = 0.0
        
        self.userStartedSpeaking = False
        self.timeStartSpeaking = 0.0
        self.timeStopSpeaking = 0.0
        
        # "./harvard.wav" also testable
        self.wavFile = "./english.wav" # the .wav file recording of the user speaking
        # list of time slices [[start, stop],...] to analyze
        self.timeSlices = [[None, None]] # [[None, None]] denotes full .wav file analysis

        self.userSpeechDict = None # dictionary of proposed transcriptions
        # [[self.r.recognize_google(audio),start,end],...]
        self.userSpeech = None # list of best guess output of transcribed speech

        ####### more variables ######
        self.chatHandler = ChatHandler()
        self.name = '' # api-key variable... so poorly named... I'm sorry.... :(
        self.userName = ''
        self.augMsg = '' # augmented message (augmentation + original message
        self.reply = '' # the response from chatbot
        self.msg = '' # the original message typed in
        self.showAugmentation = True # output the emotional augmentation being used
        self.useAugmentation = True # set to False to not use emotional augmentation
        self.ferDelay = 500 
        self.aug_dict = {'None':[""],
            'Neutral':["(Reply as if I have a neutral facial expression)"],
            'Happy':["(Reply as if I am really happy)"], 
            'Sad':["(Reply as if I am really sad)"],
            'Surprise':["(Reply as if I am really surprised)"],
            'Fear':["(Reply as if I am really scared)"],
            'Disgust':["(Reply as if I am really disgusted)"],
            'Angry':["(Reply as if I am really angry)"]}
        self.imageDict = {'None': './startImage.jpg',
            'Neutral':'./startImage.jpg',
            'Happy':'./startImage.jpg', 
            'Sad':'./startImage.jpg',
            'Surprise':'./startImage.jpg',
            'Fear':'./startImage.jpg',
            'Disgust':'./startImage.jpg',
            'Angry':'./startImage.jpg'}

        self.commandPrefix = "%%%" # prefix to enter a command to the system (see sendButton())
        # dictionary of available commanable variables and their values
        self.commandList = ['self.showAugmentation','self.useAugmentation', 'self.ferDelay']
        self.restrictAccessToCommandList = False
        
        ###################################
        #   BEGIN WINDOW CONSTRUCTION
        ###################################
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
 
        # LOGIN window setup #############################
        self.login = Toplevel()
        # set the title
        self.login.title("api-key and name")
        self.login.resizable(width=True,
                             height=True)
        self.login.configure(width=800,
                             height=300)
        # send the login window to the front
        self.login.attributes("-topmost",True)
        self.login.grab_set()
        self.login.focus()
        # create a Label for api-key
        self.pls = Label(self.login,
                         text="Please enter an api-key (or leave it blank to skip).\nThis will set the key as an environmental variable\n on your system if possible.",
                         justify=CENTER,
                         font="Helvetica 14 bold")
 
        self.pls.place(relheight=0.35,
                       relx=0.2,
                       rely=0.07)
        # entry box for api-key (or return to skip)
        self.entryName = Entry(self.login,
                               font="Helvetica 14")
 
        self.entryName.place(relwidth=0.65,
                             relheight=0.1,
                             relx=0.1,
                             rely=0.35)
 
        # create a Label for user name
        self.labelName = Label(self.login,
                               text="Enter a name you'd like to use (optional). ",
                               justify=CENTER,
                               font="Helvetica 12")
 
        self.labelName.place(relheight=0.15,
                             relx=0.1,
                             rely=0.5)

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
        self.login.bind("<Escape>",self.closeLoginWindow)

        self.go = Button(self.login,
                         text="CONTINUE",
                         font="Helvetica 14 bold",
                         command=lambda: self.beginChat(self.entryName.get(), userName = self.entryUserName.get()))
        self.go.pack() # activate the return binding
        
        self.go.place(relx=0.4,
                      rely=0.8)

        if self.client != None:
            self.Window.after(self.ferDelay, self.getCurrentFER)

        self.Window.mainloop()    
 
    # CHAT window setup #######################
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

        # server information label ###
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
        self.labelHead.place(relwidth=1,relheight=.1)

        # line between server info and chat output
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")
 
        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        # emotion image zone
        self.fer_image = Image.open(self.startImage)
        self.fer_image = ImageTk.PhotoImage(self.fer_image)
        self.imageLabel = Label(self.labelHead,
                               bg="#17202A",
                               fg="#EAECEE",
                               pady=5,image = self.fer_image)
        self.imageLabel.place(relwidth=1,
                             relx=0.35,
                             rely=0.1)
        
        self.imageLabel.pack()
        
        # line between server info and chat output
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")
 
        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)
        

        # chat OUTPUT box ####
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
        self.textCons.config(cursor="arrow") # respons to cursor keys
        self.textCons.config(state=DISABLED) # set startup state to disabled

        # setup space for chat input and send button
        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)
 
        self.labelBottom.place(relwidth=1,
                               rely=0.825)
        # chat INPUT box ####
        self.entryMsg = Text(self.labelBottom,
                              bg="#2C3E50",
                              fg="#EAECEE",
                              font="Helvetica 13")
        self.entryMsg.place(relwidth=0.72,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)
        self.entryMsg.focus()
        
        # create a Send Button
        # make it respond to 'ctrl+return' too.
        self.Window.bind("<Shift-Return>", lambda e: self.sendButton(self.entryMsg.get("1.0","end")))
        self.Window.bind("<Escape>",self.closeApp)
        self.Window.bind("<Key>", self.keyPressedEvent)
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryMsg.get("1.0","end")))
        self.buttonMsg.pack() # activate the return binding
        self.buttonMsg.place(relx=0.62,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.16)
 
        # create a microphone Button
        self.micButtonMsg = Button(self.labelBottom,
                                text="push\nto\nrecord",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.micButton())
        self.micButtonMsg.pack() # activate the return binding
        self.micButtonMsg.place(relx=0.82,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.16)
 
        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)
        scrollbar.place(relheight=1,
                        relx=0.974)
        scrollbar.config(command=self.textCons.yview)
 

    ############################################################################
    ##          End of layout 
    ##          Begin functionality

    def micButton(self):
        # if user starts speaking
        if self.userStartedSpeaking == False:
            self.timeStartSpeaking = time.time()
            self.userStartedSpeaking = True
            self.clearInputBox()
            self.entryMsg.config(state=DISABLED)
            self.buttonMsg.config(state=DISABLED)
            
            # start recording .wav file of user speaking
            self.startRecordingUser()
            
            print("user started speaking at: ", self.timeStartSpeaking)
            self.micButtonMsg["text"]="push\nto\nstop"
        else: # user stops speaking
            self.timeStopSpeaking = time.time()
            self.userStartedSpeaking = False
            self.buttonMsg.config(state=NORMAL)
            
            # stop recording .wav file of user speaking
            self.stopRecordingUser()
            
            print("user stopped speaking at: ", self.timeStopSpeaking)
            self.micButtonMsg["text"] = "push\nto\nrecord"
            print()

            # do speech analysis and output results to the chat box
            self.analyzeSpeech()
            #print(self.userSpeech)
            
            self.entryMsg.config(state=NORMAL)
            self.entryMsg.insert(END, self.userSpeech[0][0] + "\n")
            self.entryMsg.config(state=DISABLED)
            self.entryMsg.see(END) # moves to the end of the message (e.g., for insertion)
            
    def startRecordingUser(self):
        pass

    def stopRecordingUser(self):
        pass

    def clearInputBox(self):
        self.entryMsg.config(state=NORMAL)
        self.entryMsg.delete('1.0', 'end')
        #self.entryMsg.config(state=DISABLED)
            
    def analyzeSpeech(self):
        # tries to recognize the speech in self.wavFile between self.timeSlices
        # and returns self.userSpeech string output (not the time slices)
        # if self.timeSlices == [None, None], it will analyze the full .wav file
        try:
            y = DoSpeech(verbose = False) # free service for now... has limits.
            y.recognizeSpeechFromFile(self.wavFile, self.timeSlices)#,timeSlices=[[1.6, 3.987664],[None,None]])
            self.userSpeechDict = y.outputDict
            self.userSpeech = y.output
            return(self.userSpeech[0][0])
        except:
            print("\nproblem with analyzeSpeech()....\n")
            
    def keyPressedEvent(self, event):
        if self.entryMsg.cget('state') == 'disabled':
            return
        if event.keysym != "Shift_R" and event.keysym != "Shift_L":
            if self.userStartedTyping == False and self.entryMsg.cget('state') != 'disabled':
                self.userStartedTyping = True
                self.timeStartTyping = time.time()
                print("user started typing at: ", self.timeStartTyping)

    def closeApp(self, event):
        self.Window.destroy()
        #self.serverProcess.kill() 

    def closeLoginWindow(self, event):
        self.login.destroy()
        self.Window.destroy()

    def beginChat(self, name, userName = ':'): #############################
        self.login.destroy()
        self.layout(name) # api-key... poorly named variable :(
        self.userName = userName
        try:
            self.chatHandler.initializeAPI(api_key = key)
        except:
            self.chatHandler.initializeAPI(api_key = name)
            self.setAPIkeyAsEnvVar(name)
        self.chat_started = True
 
    def getCurrentFER(self, delay = None):
        if delay != None:
            self.ferDelay = delay
        if self.chat_started:
            try:
                raw_message = str(self.client.recv(1024).decode('utf-8'))
                fer_list = [result for result in raw_message.split(self.terminator) if result != '']
                self.fer_result = fer_list[-1]
                self.labelHead.config(text="Detected Emotion: " + str(self.fer_result))
                print("using...", self.imageDict[self.fer_result])
                self.imageLabel.config(image=self.imageDict[self.fer_result])
            except:
                print("no message from server")
                self.labelHead.config(text="No Server Detected: " + str(self.fer_result))
        self.Window.after(self.ferDelay, self.getCurrentFER)  # reschedule event in 2 seconds
 
    def getQueryAugmentation(self, index = 0):
        if self.fer_result in self.aug_dict:
            self.queryAug = self.aug_dict[self.fer_result][index]
        else:
            self.queryAug = None

        return self.queryAug
 
    def getLLMResponse(self, query = None): # default is to use non-augmented message
        if query is None:
            query = self.msg

        try:
            self.chatHandler.defineMessage(message=query)
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
    def setUseAumentation(self, value): # change whether or not to use emotions
        self.useAugmentation = value
        
    # function to basically start the thread for sending messages
    def sendButton(self, msg): # also gets called with binding (e.g., <Shift-Return>)
        self.textCons.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.config(state = NORMAL)
        
        self.userStartedTyping = False # user has sent a message and has not yet started typing again
        self.timeStopTyping = time.time()
        print("user stopped typing at: ", self.timeStopTyping)
        print()

        if self.commandPrefix not in self.msg:
            # get emotion, augmentation, compose with msg, and get response
            self.composeAugMsg()
            self.clearInputBox()
            if self.useAugmentation:
                self.getLLMResponse(query = self.augMsg)
            else:
                self.getLLMResponse(query = self.msg)

            # insert messages to text box
            self.textCons.config(state=NORMAL)
            if self.useAugmentation:
                if self.showAugmentation:
                    self.textCons.insert(END,
                                         "\n"+self.userName+": "+self.augMsg + "Chatbot: " + self.reply + "\n")
                else:
                    self.textCons.insert(END,
                                         "\n"+self.userName+": (----) "+self.msg + "Chatbot: " + self.reply + "\n")
            else: # if not using augmentation at all
                self.textCons.insert(END, "\n"+self.userName+": "+self.msg + "Chatbot: " + self.reply + "\n")

            self.textCons.config(state=DISABLED)
            self.textCons.see(END)

        else: # user is changing some variables with the commandPrefix     
            self.entryMsg.delete('1.0', 'end') # clean up
            self.textCons.config(state=NORMAL)

        try:
            command = self.msg.split()
            self.textCons.insert(END, "\n"+self.commandPrefix+"  SYSTEM COMMAND  "+self.commandPrefix+"\n")
            if command[1] == 'print':
                self.textCons.insert(END, command[1] +' '+ command[2] + "\n")
                self.textCons.insert(END, f'{command[2]} equal to: ' + str(eval(command[2])))
            elif command[1] == 'help':
                self.textCons.insert(END, f'the following commands should work (others *may* work):\n' + str(self.commandList))

            # other commands which may or may not be in the commandList
            elif ((self.restrictAccessToCommandList and (command[1] in self.commandList)) or \
               self.restrictAccessToCommandList == False): # use list or just try it anyway (less secure)
                exec(f'{command[1]}={command[2]}')
                self.textCons.insert(END, command[1] +"  =  "+ command[2]+"\n")
                output=f'{command[1]} now set to: '
                output=output+str(eval(command[1]))
                                    
                self.textCons.insert(END, output+'\n')
            else:
                raise Exception("command not found")
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
