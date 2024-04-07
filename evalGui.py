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

import subprocess
import sys

try:
    import tkvideo
    from tkvideo import *
    from tkvideo import tkvideo
except:
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'tkvideo'])

try: ############### need to install this beforehand
    from tkvideoutils import VideoPlayer
except:
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'tkvideoutils'])
    from tkvideoutils import VideoPlayer



PATH_TO_DATA = './test.mp4'# "C:\\Users\\emead\\Downloads\\test.mp4"


# GUI class for evaluation
class GUI_EVAL:
    def __init__(self, chatWinWidth = 400, chatWinHeight = None, minHeight = 10, ratingScale = 10):
        if chatWinHeight == None:
            chatWinHeight = chatWinWidth * .75
        if chatWinHeight <= 0:
            chatWinHeight = minHeight
        chatWinHeight = int(chatWinHeight)
        chatWinWidth = int(chatWinWidth)
        self.playerSizeX = 1280
        self.playerSizeY = 720 
        self.playerButtonSizeY = 0.5 
        self.bgColor = "#17202A"
        self.relTopOfWindow = 0.01
        self.buttonHeight = 0.05
        self.smallButtonHeight = 0.03
        self.ratingButtonWidth= 0.05
        self.symStartHeight = 0.74
        self.buffer = 0.01
        self.currentVidPath = PATH_TO_DATA
        
        ###################################
        #   BEGIN WINDOW CONSTRUCTION
        ###################################
        self.Window = Tk()
        self.Window.configure(width=chatWinWidth, height=chatWinHeight, bg=self.bgColor)

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
        self.Window.state("zoomed") # opens maximized.......
        #self.Window.attributes("-topmost",True)
        self.Window.grab_set()
        self.Window.focus()         
        self.Window.deiconify()
        self.Window.title("EVALUATION")
        self.Window.resizable(width=True,
                              height=True)
        # video and playing labels
        self.videoLabelHeight = self.relTopOfWindow
        self.videoLabel = Label(self.Window, text="watch the following video and rate the response to the query",\
                                justify=CENTER)
        self.videoLabel.place(relwidth=0.98, relheight=self.buttonHeight,\
                              relx=0.01, rely=self.videoLabelHeight)

        # video player window
        self.makeVideoWindow()

        # video player label
        self.playerLabelHeight = self.videoLabelHeight + self.buttonHeight + self.buffer
        self.playerLabel = Label(self.Window,bg=self.bgColor,\
                                 justify=CENTER)
        self.playerLabel.place(relwidth=0.56, relheight=self.playerButtonSizeY, \
                              relx=0.22, rely=self.playerLabelHeight)

        self.pathToVideo = PATH_TO_DATA
        # this is from https://pypi.org/project/tkVideoUtils/
        #self.audioPath = "./"
        #self.player = VideoPlayer(self.Window, self.pathToVideo, self.audioPath, self.playerLabel,\
        #                          size= (self.playerSizeX,self.playerSizeY) )
        # player = VideoPlayer(root, video_path, audio_path, video_label, size=(700, 500),
        #                     play_button=button, play_image=play_image, pause_image=pause_image,
        #                     slider=slider, slider_var=slider_var, keep_ratio=True, cleanup_audio=True)

        #self.player = tkvideo(self.pathToVideo,\
        #         self.playerLabel, loop = 1, size = (self.playerSizeX,self.playerSizeY))
        #self.playVideo()
        
        # re/play button
        self.playVidButton = Button(self.Window, text='re/play video',\
                                    justify=LEFT,command=lambda: self.rePlayVideo()) # left of video
        self.playVidButton.place(relwidth=0.2, relheight=self.playerButtonSizeY, \
                              relx=0.01, rely=self.playerLabelHeight)
            
        # next video button
        self.nextButton = Button(self.Window, text='next video',\
                                    justify=RIGHT,command=lambda: self.nextVideo()) # left of video
        self.nextButton.place(relwidth=0.2, relheight=self.playerButtonSizeY, \
                              relx=0.79, rely=self.playerLabelHeight)
            
        # responses and button labels
        self.queryLabelHeight = self.playerLabelHeight + self.playerButtonSizeY + self.buffer 
        self.queryLabel = Label(self.Window, text="example query",\
                                justify=CENTER)
        self.queryLabel.place(relwidth=0.98, relheight=self.buttonHeight, \
                              relx=0.01, rely=self.queryLabelHeight)
        
        self.responseLabelHeight = self.queryLabelHeight +self.buttonHeight + self.buffer
        self.responseLabel = Label(self.Window, text="example response",\
                                justify=CENTER)
        self.responseLabel.place(relwidth=0.98, relheight=self.buttonHeight, \
                              relx=0.01, rely=self.responseLabelHeight)

        # radio buttons for sympathy
        self.sympathyVar = StringVar()
        self.sympathyLabel = Label(self.Window, text="sympathyLabel",\
                                   justify=CENTER)
        self.sympathyLabel.place(relwidth=0.98, relheight=self.smallButtonHeight,\
                relx=0.01, rely=self.symStartHeight)
        for each in range(ratingScale):
            x = Radiobutton(self.Window, text=str(each+1),\
                            variable=self.sympathyVar,\
                        value=str(each+1),tristatevalue=0,\
                            command=self.recordSympathyValue)
            x.place(relwidth=self.ratingButtonWidth,relheight=self.smallButtonHeight,\
                    relx=.01+(each*(1/ratingScale)),\
                    rely=self.symStartHeight+self.smallButtonHeight+.01)
            
        self.appStartHeight = self.symStartHeight + (self.smallButtonHeight*2) + (self.buffer*2)
        # radio buttons for appropriateness
        self.appropriatenessVar = StringVar()
        self.appropriatenessLabel = Label(self.Window, text="appropriatenessLabel",\
                                   justify=CENTER)
        self.appropriatenessLabel.place(relwidth=0.98, relheight=self.smallButtonHeight,\
                relx=0.01, rely=self.appStartHeight)
        for each in range(ratingScale):
            x = Radiobutton(self.Window, text=str(each+1),\
                            variable=self.appropriatenessVar,\
                        value=str(each+1),tristatevalue=0,\
                            command=self.recordAppropriatenessValue)
            x.place(relwidth=self.ratingButtonWidth,relheight=self.smallButtonHeight,\
                    relx=.01+(each*(1/ratingScale)),\
                    rely=self.appStartHeight+self.smallButtonHeight+.01)

        self.undStartHeight = self.appStartHeight +  (self.smallButtonHeight*2) + (self.buffer*2)
        # radio buttons for understanding evident
        self.understandVar = StringVar()
        self.appropriatenessLabel = Label(self.Window, text="understandingLabel",\
                                   justify=CENTER)
        self.appropriatenessLabel.place(relwidth=0.98, relheight=self.smallButtonHeight,\
                relx=0.01, rely=self.undStartHeight)
        for each in range(ratingScale):
            x = Radiobutton(self.Window, text=str(each+1),\
                            variable=self.understandVar,\
                        value=str(each+1),tristatevalue=0,\
                            command=self.recordUnderstandValue)
            x.place(relwidth=self.ratingButtonWidth,relheight=self.smallButtonHeight,\
                    relx=.01+(each*(1/ratingScale)),\
                    rely=self.undStartHeight+self.smallButtonHeight+.01)



        self.Window.mainloop()

    def makeVideoWindow(self, pathToVideo = None, chatWinWidth = 600, chatWinHeight = 300, minHeight = 10, ratingScale = 10):
        if pathToVideo == None:
            pathToVideo = self.currentVidPath
        self.videoWindow = Toplevel()
        self.videoWindow.configure(width=chatWinWidth, height=chatWinHeight, bg=self.bgColor)

        # center it
        screenWidth = self.videoWindow.winfo_screenwidth()
        screenHeight = self.videoWindow.winfo_screenheight()
        winXpos = int((screenWidth-chatWinWidth)/2)
        winYpos = int(((screenHeight-chatWinHeight)/2)-150)#subtract a little for quick start bar
        if winYpos < 0:
            winYpos = 0
        if winXpos < 0:
            winXpos = 0

        geoString = str(chatWinWidth)+"x"+str(chatWinHeight)+ \
                        "+"+str(winXpos)+"+"+str(winYpos)
        self.videoWindow.geometry(geoString)
        self.videoWindow.attributes("-topmost",True)
        #self.videoWindow.grab_set()
        self.videoWindow.focus()         
        self.videoWindow.deiconify()
        self.videoWindow.title("Video Player")
        self.videoWindow.resizable(width=True,
                              height=True)
        # video player 
        self.playerLabel = Label(self.videoWindow,\
                                 justify=CENTER, text="loading")
        self.playerLabel.place(relwidth=0.98, relheight=0.98, \
                              relx=0.01, rely=0.01)
        self.setVideo(pathToVideo)
        self.playVideo()
        
    def setVideo(self, newVideo = None):
        if newVideo == None:
            newVideo = self.currentVidPath
        self.player = tkvideo(newVideo,\
                 self.playerLabel, loop = 1, size = (self.playerSizeX,self.playerSizeY))
    def playVideo(self):
        self.player.play()
    def rePlayVideo(self):
        self.nextVideo(newVideo = self.currentVidPath)
    def nextVideo(self, newVideo = './sample.mp4'):
        self.videoWindow.destroy()
        self.makeVideoWindow(pathToVideo = newVideo)
        self.playVideo()
        
    def changeQuery(self, newText = "changed"):
        self.queryLabel["text"]=newText
        self.queryLabel.update()
    def changeResponse(self, newText = "changed"):
        self.responseLabel["text"]=newText
        self.responseLabel.update()
    def recordSympathyValue(self):
        self.changeQuery()
    def recordAppropriatenessValue(self):
        print(self.appropriatenessVar.get())
    def recordUnderstandValue(self):
        self.changeResponse()
'''        # send the login window to the front
 
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

            
            

    def convertAudioDataToWavFile(self, audio, filename = "./test.wav"):
        with  open(filename, "wb") as f:
            f.write(audio.get_wav_data())
        return(filename)
                
    def closeApp(self, event):
        self.Window.destroy()
'''

def main():
    evalWin = GUI_EVAL()
    pass

if __name__ == "__main__":
    main()
