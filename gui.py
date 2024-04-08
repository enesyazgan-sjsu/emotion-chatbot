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
from multiprocessing.pool import ThreadPool
from dataHandler import DATA

# run videostream_loop.py in a cmd window before you run this
# or have autoSpawnServer try to run it for you
useServer = True     # set to false to run GUI only

autoSpawnServer = True # set false to run the server yourself


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



if autoSpawnServer == True:
    # This will attempt to run the server for you in a (new) cmd window... please wait.
    try:
        pathToVideoStreamLoop = 'start python ./videostream_loop.py' 
        if useServer:
            print("starting server...")
            # run videostream_loop.py
            import subprocess
            import sys

            serverProcess = subprocess.Popen(pathToVideoStreamLoop, stdout=subprocess.PIPE, shell=True) 
            # I want to resize the window!!! But this doesn't work... :(
            #serverProcess = subprocess.Popen('cmd','/c', 'mode con cols=100 lines=40')
            #subprocess.Popen(pathToVideoStreamLoop, shell=True) 
            print("waiting for server to start...")
            time.sleep(10)
            print("done waiting...")
    except Exception as e:
        print(e)
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
            self.serverProcess = None
        else:
            self.usingServer = True
            self.serverProcess = serverProcess
        self.client = client
        self.terminator = "#" # between time stamp and next emotion
        self.termTime = "%" # between emotion and time stamp
        self.chat_started = False
        # emotional results variables
        self.ferHistResults = [] # history or results [[str(emotion), str(timeStamp)],...]
        self.fer_result = "None" # str(emotion)
        self.fer_image = './startImage.jpg' # image to display for a given fer_result
        # setup time slices and multiple emotions in EAR
        self.useSpeakType = 'type' # 'speak' or 'type' to choose which input to use

        self.useMultEAR = False # use multiple emotions in EAR 
        
        self.userStartedTyping = False
        self.timeStartTyping = 0.0
        self.timeStopTyping = 0.0
        
        self.userStartedSpeaking = False
        self.timeStartSpeaking = 0.0
        self.timeStopSpeaking = 0.0
        self.speakTrigger = [250,150] # frequency and duration of the "speak" tone trigger
        self.nothingWasHeard = False # marks when no speech was heard
        
        # "./harvard.wav" also testable
        self.wavFile = "./english.wav" # the .wav file recording of the user speaking
        # list of time slices [[start, stop],...] to analyze
        self.timeSlices = [[None, None]] # [[None, None]] denotes full .wav file analysis

        self.userSpeechDict = None # dictionary of GoogleSpeech proposed transcriptions
        # [[self.r.recognize_google(audio),start,end],...]
        self.userSpeech = None # list of best guess output of transcribed speech
        self.speechTimeout = 3 # seconds speech analyzer will wait for speech to start

        ####### more variables ######
        self.chatHandler = ChatHandler()
        self.apiKey = '' # api-key variable
        self.userName = ''
        self.augMsg = '' # augmented message (augmentation + original message
        self.reply = '' # the response from chatbot
        self.msg = '' # the original message typed in
        self.showAugmentation = True # output the emotional augmentation being used
        self.useAugmentation = True # set to False to not use emotional augmentation
        self.ferDelay = 7500

        self.emotionList = ['Neutral', 'Happy', 'Sad', 'Surprise', 'Fear', 'Disgust', 'Angry']
        self.aug_dict = {}
        # fill emotion dictionary with templates........
        for each in self.emotionList:
            self.aug_dict[each] = []
            self.aug_dict[each].append(f"(Reply as if I have a {each} facial expression.)")
            self.aug_dict[each].append(f"(I am {each} now.)")
            self.aug_dict[each].append(f"(Reply as if you see that I have a {each} facial expression.)")
        # account for None emotion as well
        self.aug_dict['None'] = []
        for each in range(len(self.aug_dict[self.emotionList[0]])):
            self.aug_dict['None'].append("")
        # index to use for default template
        self.EARindex = 2 # which in the list of augmentations to use

        self.imageFolder = "./emotionImages/"
        self.startImage = self.imageFolder + 'startImage.png' # image to display for a given fer_result
        self.imageDict = {'None': self.imageFolder+'startImage.png',
            'Neutral':self.imageFolder+'Neutral.png',
            'Happy':self.imageFolder+ 'Happy.png', 
            'Sad':self.imageFolder+ 'Sad.png',
            'Surprise':self.imageFolder+'Surprise.png',
            'Fear':self.imageFolder+'Fear.png',
            'Disgust':self.imageFolder+'Disgust.png',
            'Angry':self.imageFolder+'Angry.png'}

        self.commandPrefix = "%%%" # prefix to enter a command to the system (see sendButton())
        # dictionary of available commanable variables and their values
        self.commandList = ['self.showAugmentation','self.useAugmentation', 'self.ferDelay']
        self.restrictAccessToCommandList = False
        self.currentDataPath = './tempDataSave.txt'
        
        ###################################
        #   BEGIN WINDOW CONSTRUCTION
        ###################################
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        # center it
        screenWidth = self.Window.winfo_screenwidth()
        screenHeight = self.Window.winfo_screenheight()
        winXpos = int((screenWidth-50)/2)
        winYpos = int(((screenHeight-50)/2)-50)#subtract a little for quick start bar
        if winYpos < 0:
            winYpos = 0
        if winXpos < 0:
            winXpos = 0
        geoString = str(50)+"x"+str(50)+ \
                        "+"+str(winXpos)+"+"+str(winYpos)
        self.Window.geometry(geoString)
 
        # LOGIN window setup #############################
        self.login = Toplevel()

        self.loginWidth = 800
        self.loginHeight = 300
        # set the title
        self.login.title("api-key and name")
        self.login.resizable(width=True,
                             height=True)
        self.login.configure(width=self.loginWidth,
                             height=self.loginHeight)
        # center it
        screenWidth = self.login.winfo_screenwidth()
        screenHeight = self.login.winfo_screenheight()
        winXpos = int((screenWidth-self.loginWidth)/2)
        winYpos = int(((screenHeight-self.loginHeight)/2)-50)#subtract a little for quick start bar
        if winYpos < 0:
            winYpos = 0
        if winXpos < 0:
            winXpos = 0
        geoString = str(self.loginWidth)+"x"+str(self.loginHeight)+ \
                        "+"+str(winXpos)+"+"+str(winYpos)
        self.login.geometry(geoString)

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
 
        self.entryName.place(relwidth=0.57,
                             relheight=0.1,
                             relx=0.2,
                             rely=0.37)
 
        # create a Label for user name
        self.labelName = Label(self.login,
                               text="Enter a name you'd like to use (optional). ",
                               justify=CENTER,
                               font="Helvetica 12")
 
        self.labelName.place(relheight=0.15,
                             relx=0.3,
                             rely=0.5)

        # create a entry box for user name 
        self.entryUserName = Entry(self.login,
                               font="Helvetica 14")
 
        self.entryUserName.place(relwidth=0.2,
                             relheight=0.12,
                             relx=0.37,
                             rely=0.62)
 
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
        #self.go.pack() # activate the return binding
        
        self.go.place(relx=0.4,
                      rely=0.8)

        if self.client != None:
            self.Window.after(self.ferDelay, self.getCurrentFER)

        self.Window.mainloop()    
 
    # CHAT window setup #######################
    def layout(self, api_key, chatWinWidth = 470, chatWinHeight=550):
 
        self.apiKey = api_key
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=True,
                              height=True)
        self.Window.configure(width=chatWinWidth,
                              height=chatWinHeight,
                              bg="#17202A")
        # center it
        screenWidth = self.Window.winfo_screenwidth()
        screenHeight = self.Window.winfo_screenheight()
        winXpos = int((screenWidth-chatWinWidth)/2)
        winYpos = int(((screenHeight-chatWinHeight)/2)-50)#subtract a little for quick start bar
        if winYpos < 0:
            winYpos = 0
        if winXpos < 0:
            winXpos = 0
        geoString = str(chatWinWidth)+"x"+str(chatWinHeight)+ \
                        "+"+str(winXpos)+"+"+str(winYpos)
        self.Window.geometry(geoString)
        self.Window.state("zoomed")

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
        # load the imageDict with PhotoImage objects for use later to update label image
        for each in self.imageDict.keys():
            try:
                self.fer_image = Image.open(self.imageDict[each])
                self.fer_image = ImageTk.PhotoImage(self.fer_image)
                self.imageDict[each] = self.fer_image
            except Exception as e:
                print (e)
                print("problem loading image: ", each, "...")

        self.fer_image = Image.open(self.startImage)
        self.fer_image = ImageTk.PhotoImage(self.fer_image)
        self.imageLabel = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               image = self.fer_image)
        self.imageLabel['bg']=self.imageLabel.master['bg']
        self.imageLabel.place(relwidth=1,
                             relx=0.0,
                             rely=0.09, relheight = .20)
        
        # chat OUTPUT box ####
        self.textCons = Text(self.Window,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)
 
        self.textCons.place(relheight=0.5,
                            relwidth=1,
                            rely=0.3)
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
        self.entryMsg.place(relwidth=0.7,
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
        #self.buttonMsg.pack() # activate the return binding
        self.buttonMsg.place(relx=0.72,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.14)
 
        # create a microphone Button
        self.micButtonMsg = Button(self.labelBottom,
                                text="push\nto\nspeak",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.micButton())
        #self.micButtonMsg.pack() # activate the return binding
        self.micButtonMsg.place(relx=0.89,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.1)
 
        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)
        scrollbar.place(relheight=.95,
                        relx=0.974)
        scrollbar.config(command=self.textCons.yview)

        # make a recording checkbox
        self.recordVar = IntVar()
        self.recordCheckbutton = Checkbutton(self.labelBottom, \
                    text = 'record/add data to: '+self.currentDataPath,\
                    variable=self.recordVar, onvalue=1, offval=0)
        self.recordCheckbutton.place(relx=0.01,
                             rely=0.076,
                             relheight=0.02,
                             relwidth=0.98)
        
    ############################################################################
    ##          End of layout 
    ##          Begin functionality

    def micButton(self):
        # if user starts speaking
        if self.userStartedSpeaking == False:

            self.useSpeakType = 'speak' # set system to use spoken input
            self.nothingWasHeard = False # reset this
            
            self.timeStartSpeaking = time.time()
            self.ferHistResults = [] # clear history to capture this session's emotions
            self.userStartedSpeaking = True
            self.clearInputBox()
            self.entryMsg.config(state=DISABLED)
            self.buttonMsg.config(state=DISABLED)
            # stop the clock on any typing that may have been happening
            if self.userStartedTyping == True:
                self.userStartedTyping = False # user has sent a message and has not yet started typing again
                self.timeStopTyping = time.time()
                print("user aborted typing at: ", self.timeStopTyping)
            
            # start recording .wav file of user speaking
            self.startRecordingUser()
            
            print("user started speaking at: ", self.timeStartSpeaking)
            self.micButtonMsg["text"]="wait\nfor\nbeep"
            self.micButtonMsg.config(state=DISABLED)
            self.micButtonMsg.update()
            
            #time.sleep(.5) # *may* need this to allow the interface to update
            
            ################################################################################
            # temporarily only gets input from mic and does not record #####################
            self.userStartedSpeaking = True
            #self.analyzeSpeech()#fromFile = False) # need to run this as a subprocess............................................

            # send voice analysis into a separate thread (cleans up after itself too)
            pool=ThreadPool(processes=1)
            print("sending analyzeSpeech")
            async_result = pool.apply_async(self.analyzeSpeech)

            # speech analysis should continue until ready to rejoin
            # analyzeSpeech handles the refresh of the interface
            ################################################################################
            
            
    def startRecordingUser(self):
        pass

    def stopRecordingUser(self):
        pass

    def clearInputBox(self):
        self.entryMsg.config(state=NORMAL)
        self.entryMsg.delete('1.0', 'end')
        #self.entryMsg.config(state=DISABLED)

    def convertAudioDataToWavFile(self, audio, filename = "./test.wav"):
        with  open(filename, "wb") as f:
            f.write(audio.get_wav_data())
        return(filename)
                   


    def analyzeSpeech(self, fromFile = False):
        # tries to recognize the speech in self.wavFile between self.timeSlices
        # and returns self.userSpeech string output (not the time slices)
        # if self.timeSlices == [None, None], it will analyze the full .wav file
        try:
            y = DoSpeech(verbose = False) # free service for now... has limits.
            if fromFile == False:
                try:
                    audioDataOutput = y.recognizeSpeechFromMic(self.speakTrigger, timeout = self.speechTimeout) # send a freq and duration of 500 and 250 to trigger speaking
                    self.wavFile = self.convertAudioDataToWavFile(audioDataOutput)
                except Exception as e:
                    print("problem with analyze speech...")
                    print(e)
            else:
                y.recognizeSpeechFromFile(self.wavFile, self.timeSlices)#,timeSlices=[[1.6, 3.987664],[None,None]])
            self.userSpeechDict = y.outputDict
            self.userSpeech = y.output
            try:
                returnString = self.userSpeech[0][0]
            except: # didn't find any speech...
                returnString = ""
                
            #############################################################
            # user stops speaking - reset everything
            self.timeStopSpeaking = time.time()
            self.userStartedSpeaking = False
            self.buttonMsg.config(state=NORMAL)
            self.micButtonMsg.config(state=NORMAL)
            self.micButtonMsg["text"] = "push\nto\nspeak"
            self.micButtonMsg.update()
            
            # stop recording .wav file of user speaking
            self.stopRecordingUser()
            
            print("user stopped speaking at: ", self.timeStopSpeaking)
            print(self.ferHistResults)
            print()

            # put output into chat window input space for review
            self.entryMsg.config(state=NORMAL)
            try:
                self.entryMsg.insert(END, self.userSpeech[0][0] + "\n")
                self.entryMsg.config(state=DISABLED) # keep message un-editable until send
                self.entryMsg.see(END) # moves to the end of the message (e.g., for insertion)
            except Exception as e:
                # nothing was saved into userSpeech because nothing was recognized
                self.entryMsg.config(state=NORMAL) # keep message un-editable until send
                self.entryMsg.see(END) # moves to the end of the message (e.g., for insertion)

            return(returnString)
        
        except Exception as e:
            print(e)
            print("\nproblem with analyzeSpeech()....\n")
            
    def keyPressedEvent(self, event):
        if self.entryMsg.cget('state') == 'disabled':
            return
        if event.keysym != "Shift_R" and event.keysym != "Shift_L":
            self.useSpeakType = 'type'
            if self.userStartedTyping == False and self.entryMsg.cget('state') != 'disabled':
                self.ferHistResults = [] # clear the emotion list to get emotions only for this session
                self.userStartedTyping = True
                self.timeStartTyping = time.time()
                print("user started typing at: ", self.timeStartTyping)
                self.timeStopTyping = time.time() # keep this up to the last key pressed
            else:
                self.timeStopTyping = time.time() # keep this up to the last key pressed
                
    def closeApp(self, event):
        self.Window.destroy()
        #self.serverProcess.kill() 

    def closeLoginWindow(self, event):
        self.login.destroy()
        self.Window.destroy()

    def beginChat(self, apiKeyString, userName = ':'): #############################
        self.login.destroy()
        self.layout(apiKeyString) # api-key
        self.userName = userName
        try:
            self.chatHandler.initializeAPI(api_key = key)
        except:
            self.chatHandler.initializeAPI(api_key = apiKeyString)
            self.setAPIkeyAsEnvVar(apiKeyString)
        self.chat_started = True
 
    def getCurrentFER(self, delay = None):
        # gets list of emotions and time stamps
        if delay != None:
            self.ferDelay = delay
        if self.chat_started:
            try:
                raw_message = str(self.client.recv(1024).decode('utf-8'))
                #print(raw_message) # "happy#17286487.8278%" # self.termTime is event delimiter
                # should get [happy#183764786.632%sad#827635987.872635...]
                fer_list = [result for result in raw_message.split(self.termTime) if result != '']
                ferTime = fer_list[-1].split(self.terminator) # ['Angry', '1710025315.6787279']
                self.ferHistResults.append(ferTime) # historical emotions with time stamps
                self.fer_result = ferTime[0] # 'Angry'
                self.labelHead.config(text="Detected Emotion: " + str(self.fer_result))
            except Exception as e:
                print(e)
                print("no message from server")
                self.labelHead.config(text="No Server Detected: " + str(self.fer_result))
            # set emotion image on screen label
            try:
                #print("using...", self.fer_result)
                #print("using...", self.imageDict[self.fer_result])
                self.imageLabel.config(image=self.imageDict[self.fer_result])
            except Exception as e:
                print(e)
                print("problem loading image onto label...")
                pass
        self.Window.after(self.ferDelay, self.getCurrentFER)  # reschedule event in 2 seconds
 
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

    def getQueryAugmentation(self, index = None):
        if index != None: # index into augmentation dictionary
            self.EARindex = index

        try:
            if self.fer_result in self.aug_dict:
                self.queryAug = self.aug_dict[self.fer_result][self.EARindex]
            else:
                self.queryAug = None
        except Exception as e:
            print(e)
            pass
        
        return self.queryAug

    def composeMultQueryAugMsg(self, index = None):
        # self.useMultEAR == True will use multiple emotions within a query
        # return msg with emotional augmentations per interval
        if index != None: # index into augmentation dictionary
            self.EARindex = index
        finalMsg = ""
        ferList = [] # list of emotions per input session
        epi = 0 # emotions per input session
        startTime = 0.0
        endTime = 0.0
        # determine how many emotions were reported during input
        if self.useSpeakType == 'type':
            startTime = float(self.timeStartTyping)
            endTime = float(self.timeStopTyping)
        else:
            startTime = float(self.timeStartSpeaking)
            endTime = float(self.timeStopSpeaking)
            
        for each in self.ferHistResults:
            if float(each[1]) >= startTime and float(each[1]) <= endTime:
                ferList.append(each)
                        
        # split input message into pieces of fraction size
        listOfWordsInMsg = self.msg.split(' ') # default to space separations
        if len(ferList) == 0.0:
            ferList.append(['None', str(endTime)]) # filler in the case of no fer
        wordsPerEmotion = int(len(listOfWordsInMsg) / len(ferList))

        wordIndex = 0
        # get augmentations for each and stitch together
        for eachEmotion in ferList: # ['Happy', '283746782.62738']
            finalMsg = finalMsg + ' ' + self.aug_dict[eachEmotion[0]][self.EARindex]
            for eachWord in range(wordIndex, wordIndex + wordsPerEmotion):
                try:
                    finalMsg = finalMsg + ' ' + listOfWordsInMsg[eachWord]
                except:
                    pass # numbers didn't line up, passed the end of the message
            wordIndex = wordIndex + wordsPerEmotion
        finalMsg = finalMsg + "\n\n"
        # return complete multiple EAR response
        return(finalMsg)
        
    def composeAugMsg(self):
        if self.useMultEAR:
            self.augMsg = self.composeMultQueryAugMsg()
        else:
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
        #self.timeStopTyping = time.time()
        if self.useSpeakType == 'type':
            print("user stopped typing this message at: ", self.timeStopTyping)
        else:
            print("user stopped speaking this message at: ", self.timeStopSpeaking)
        print(self.ferHistResults)            
        print()

        if self.commandPrefix not in self.msg:
            # get emotion, augmentation, compose with msg,
            # get response, and record data if enabled
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

            # record data if enabled #######################
            if self.recordVar.get() == 1:
                self.recordData()
                
            

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
            self.nothingWasHeard = True
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            
        # reset input mode to type (until mic is pressed again)
        self.useSpeakType = 'type'

    def recordData(self):
        print("recording data and appending it to: ", self.currentDataPath)
        # timestampStart|+|45||vidPath|+|./test.mp4||origQuery|+|hello||augQuery|+|hello(happy)||origResponse|+|yes?||augResponse|+|you seem happy!\n
        kvDelim = '|+|'
        elDelim = '||'
        timeStartSpeaking = str(int(float(self.timeStartSpeaking)))
        timeStopSpeaking = str(int(float(self.timeStopSpeaking)))
        timeStartTyping = str(int(float(self.timeStartTyping)))
        timeStopTyping = str(int(float(self.timeStopTyping)))
        if self.useSpeakType == 'type':
            # int portion of start-stop time stamp
            ts = timeStartTyping+'-'+timeStopTyping
        else:
            ts = timeStartSpeaking+'-'+timeStopTyping
            
        vp = './NEEDS_TO_BE_DONE' # path to video
        oq = self.msg.replace('\n','\\n') # original query
        aq = self.augMsg.replace('\n','\\n') # augmented query
        orr = 'NEEDS_TO_BE_DONE' # original response
        ar = self.reply.replace('\n','\\n') # augmented response
        
        dataString = 'timestampStart' + kvDelim + ts +\
                     elDelim + 'vidPath' + kvDelim + vp +\
                     elDelim + 'origQuery' + kvDelim + oq +\
                     elDelim + 'augQuery' + kvDelim + aq +\
                     elDelim + 'origResponse' + kvDelim + orr +\
                     elDelim + 'augResponse' + kvDelim + ar + '\n'
                     
        # if file exists, append data to it
        if not os.path.isfile(self.currentDataPath):
            with open(self.currentDataPath,'w') as f:
                f.write(dataString)
        else:
            with open(self.currentDataPath, 'a') as f:
                f.write(dataString)

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
