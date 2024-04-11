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
 
import subprocess
import sys

try:
    import tkvideo
    from tkvideo import *
    from tkvideo import tkvideo
except:
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'tkvideo'])

PATH_TO_OBSERVER_DATA = './observerData.txt' # appends observer judgements to this file
DATA_PATH = './tempDataSave.txt' # reads in video paths, queries, responses, etc. from this file

# GUI_EVAL class for evaluation
class GUI_EVAL:
    def __init__(self, chatWinWidth = 400, chatWinHeight = None, minHeight = 10, ratingScale = 10, \
                 dataPath = None, observerDataPath = None):
        if observerDataPath == None:
            self.observerDataPath = PATH_TO_OBSERVER_DATA
        else:
            self.observerDataPath = observerDataPath
        if dataPath == None:
            dataPath = DATA_PATH
        self.data = DATA(dataPath)
        self.dataKeyIter = iter(self.data.dataDict.keys()) # time stamps iterator
        
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
        # find first timestamp and video path
        self.currentDataTS = next(self.dataKeyIter, None)
        self.currentVidPath = self.data.dataDict[self.currentDataTS]['vidPath']
        self.outOfData = False
        self.cantFindVideo = False

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

        # This may be useful if we need to change video players.....?????
        #PATH_TO_DATA = './test.mp4'# "C:\\Users\\emead\\Downloads\\test.mp4"
        #self.pathToVideo = PATH_TO_DATA
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
        self.symButList = []
        self.sympathyVar = StringVar()
        self.sympathyLabel = Label(self.Window, text="sympathy",\
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
            self.symButList.append(x)
            
        self.appStartHeight = self.symStartHeight + (self.smallButtonHeight*2) + (self.buffer*2)
        # radio buttons for appropriateness
        self.appButList = []
        self.appropriatenessVar = StringVar()
        self.appropriatenessLabel = Label(self.Window, text="appropriateness",\
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
            self.appButList.append(x)
            
        self.undStartHeight = self.appStartHeight +  (self.smallButtonHeight*2) + (self.buffer*2)
        # radio buttons for understanding evident
        self.undButList = []
        self.understandVar = StringVar()
        self.appropriatenessLabel = Label(self.Window, text="understanding",\
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
            self.undButList.append(x)

        self.Window.bind("<Escape>",self.closeEvalGui)
        self.Window.mainloop()

    def closeEvalGui(self,event):
        self.videoWindow.destroy()
        self.Window.destroy()

    def makeVideoWindow(self, pathToVideo = None, chatWinWidth = 600, chatWinHeight = 300, minHeight = 10, ratingScale = 10):
        if pathToVideo == None:
            if self.currentVidPath == None:
                # reached end of available data in DATA
                print("out of data... aborting video play...")
                self.videoWindow.destroy()
                self.currentVidPath = None
                self.makeVideoWindow(pathToVideo="Video Player")
                return
            pathToVideo = self.currentVidPath
            
        self.videoWindow = Toplevel()
        self.videoWindow.configure(width=chatWinWidth, height=chatWinHeight, bg=self.bgColor)
        blankText = 'loading'
        if pathToVideo == "Video Player":
            blankText = 'Video Player'
        # center it
        screenWidth = self.videoWindow.winfo_screenwidth()
        screenHeight = self.videoWindow.winfo_screenheight()
        winXpos = int((screenWidth-chatWinWidth)/2)
        winYpos = int(((screenHeight-chatWinHeight)/2)-150)#subtract a little for quick start bar
        if winYpos < 0:
            winYpos = 0
        if winXpos < 0:
            winXpos = 0

        # for use later
        self.chatWinWidth=chatWinWidth
        self.chatWinHeight=chatWinHeight
        self.winXpos=winXpos
        self.winYpos=winYpos
        
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
                                 justify=CENTER, text=blankText)
        self.playerLabel.place(relwidth=0.98, relheight=0.98, \
                              relx=0.01, rely=0.01)
        if pathToVideo != "Video Player":
            self.setVideo(pathToVideo)
            self.playVideo()
        
    def setVideo(self, newVideo = None):
        if newVideo == None:
            newVideo = self.currentVidPath
        self.player = tkvideo(newVideo,\
                 self.playerLabel, loop = 0, size = (self.playerSizeX,self.playerSizeY))
        
    def playVideo(self):
        if os.path.isfile(self.currentVidPath):
            if self.outOfData == False:
                self.cantFindVideo = False
            self.player.play()
        else:
            print("Can't find video...")
            self.playerLabel['text'] = 'trouble finding video - press next video'
            self.cantFindVideo = True
        
    def rePlayVideo(self):
        self.resetButtons()
        self.videoWindow.destroy()
        self.makeVideoWindow()
        self.playVideo()
        
    def resetButtons(self):
        for each in self.symButList:
            each.deselect()
        for each in self.appButList:
            each.deselect()
        for each in self.undButList:
            each.deselect()
        print(self.sympathyVar.get(), self.appropriatenessVar.get(), self.understandVar.get())

    def recordObserverData(self):
        print("recording observer ratings and appending it to: ", self.observerDataPath)
        # timestampStart|+|45||vidPath|+|./test.mp4||origQuery|+|hello||augQuery|+|hello(happy)||origResponse|+|yes?||augResponse|+|you seem happy!\n
        kvDelim = '|+|'
        elDelim = '||'
        ts = str(self.currentDataTS)
        symResp = self.sympathyVar.get()
        appResp = self.appropriatenessVar.get()
        undResp = self.understandVar.get()

        dataString = 'timestampStart' + kvDelim + ts +\
                     elDelim + 'symResp' + kvDelim + symResp +\
                     elDelim + 'appResp' + kvDelim + appResp +\
                     elDelim + 'undResp' + kvDelim + undResp + '\n'

        # if file exists, append data to it
        if not os.path.isfile(self.observerDataPath):
            with open(self.observerDataPath,'w') as f:
                f.write(dataString)
        else:
            with open(self.observerDataPath, 'a') as f:
                f.write(dataString)

    def nextVideo(self, newVideo = None):
        try:
            if (int(self.appropriatenessVar.get()) > 0 and int(self.sympathyVar.get()) > 0 and \
                               int(self.understandVar.get()) > 0) or self.cantFindVideo == True:
                print(self.sympathyVar.get(), self.appropriatenessVar.get(), self.understandVar.get())
                try:
                    if self.outOfData == False and self.cantFindVideo == False:
                        self.recordObserverData()
                except Exception as e:
                    print(e)
                    
                if newVideo == None:
                    # find next timestamp and video path
                    self.currentDataTS = next(self.dataKeyIter, None)
                    if self.currentDataTS == None:
                        print("reached the end of the data... aborting video playback...")
                        self.outOfData = True
                        self.videoWindow.destroy()
                        self.makeVideoWindow(pathToVideo = 'Video Player')
                        # update buttons
                        self.changeQuery('example query')
                        self.changeResponse('example response')
                    else:
                        # set new video playing
                        self.currentVidPath = self.data.dataDict[self.currentDataTS]['vidPath']                            
                        newVideo = self.currentVidPath
                        print("loading: ",newVideo)
                        # update buttons
                        self.changeQuery(self.data.dataDict[self.currentDataTS]['origQuery'])
                        self.changeResponse(self.data.dataDict[self.currentDataTS]['augResponse'])

                        self.videoWindow.destroy()
                        self.currentVidPath = newVideo
                        self.makeVideoWindow(pathToVideo = newVideo)
                        self.playVideo()
                    self.resetButtons() # clear user's choices off radio buttons
        except Exception as e:            
            from tkinter import messagebox
            geoString = str(self.chatWinWidth)+"x"+str(self.chatWinHeight-200)+ \
                            "+"+str(self.winXpos)+"+"+str(self.winYpos)
            self.videoWindow.geometry(geoString)

            eraseMessages = messagebox.showinfo(message="you must rate the video for all aspects \nbefore moving on to the next video", title="WARNING")

            geoString = str(self.chatWinWidth)+"x"+str(self.chatWinHeight)+ \
                            "+"+str(self.winXpos)+"+"+str(self.winYpos)
            self.videoWindow.geometry(geoString)

    def changeQuery(self, newText = "changed"):
        self.queryLabel["text"]=newText
        self.queryLabel.update()
    def changeResponse(self, newText = "changed"):
        self.responseLabel["text"]=newText
        self.responseLabel.update()
    def recordSympathyValue(self):
        pass
    def recordAppropriatenessValue(self):
        pass
    def recordUnderstandValue(self):
        pass

def main():
    evalWin = GUI_EVAL()

if __name__ == "__main__":
    main()
