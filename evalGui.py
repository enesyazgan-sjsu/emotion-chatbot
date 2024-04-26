#import time
#import socket
#import openai
#from chatHandler import ChatHandler
#from DoSpeech import DoSpeech
#from PIL import Image, ImageTk
#from multiprocessing.pool import ThreadPool

import os
from tkinter import *
import tkinter.messagebox
from dataHandler import DATA
import random


try:
    import tkvideo
    from tkvideo import *
    from tkvideo import tkvideo
except:
    import subprocess
    import sys
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'tkvideo'])
    import tkvideo
    from tkvideo import *
    from tkvideo import tkvideo

PATH_TO_OBSERVER_DATA = './observerData.txt' # appends observer judgements to this file
DATA_PATH = './tempDataSave.txt' # reads in video paths, queries, responses, etc. from this file

# GUI_EVAL class for evaluation
class GUI_EVAL:
    def __init__(self, chatWinWidth = 400, chatWinHeight = None, minHeight = 10, ratingScale = 5, \
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
        self.smallButtonHeight = 0.02
        self.ratingButtonWidth= 0.05
        self.symStartHeight = 0.72
        self.buffer = 0.01
        # find first timestamp and video path
        self.currentDataTS = next(self.dataKeyIter, None)
        self.currentVidPath = self.data.dataDict[self.currentDataTS]['vidPath']
        self.outOfData = False
        self.cantFindVideo = False
        self.randomizeResponse = True # observer sees a random mix of augmented and baseline
        self.seeAugResp = True
        self.randVal = 6
        if self.randomizeResponse and (random.randint(1,10) > self.randVal):
            self.randomizeResp()
        
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
        tq = self.data.dataDict[self.currentDataTS]['origQuery']
        self.queryLabel = Label(self.Window, text=tq,\
                                justify=CENTER)
        self.queryLabel.place(relwidth=0.98, relheight=self.buttonHeight, \
                              relx=0.01, rely=self.queryLabelHeight)
        
        self.responseLabelHeight = self.queryLabelHeight +self.buttonHeight + self.buffer
        tr = self.data.dataDict[self.currentDataTS]['augResponse']
        if self.randomizeResponse and (self.seeAugResp == False):
            tr = self.data.dataDict[self.currentDataTS]['origResponse']
        self.responseLabel = Label(self.Window, text=tr,\
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
            
        self.undStartHeight = self.appStartHeight +  \
                              (self.smallButtonHeight*2) + \
                              (self.buffer*2)
        # radio buttons for understanding evident
        self.undButList = []
        self.understandVar = StringVar()
        self.understandingLabel = Label(self.Window, text="understanding",\
                                   justify=CENTER)
        self.understandingLabel.place(relwidth=0.98, relheight=self.smallButtonHeight,\
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

        self.ovlStartHeight = self.undStartHeight + \
                              (self.smallButtonHeight*2) + \
                              (self.buffer*2)
        #self.undStartHeight = self.appStartHeight +  (self.smallButtonHeight*2) + (self.buffer*2)
        # radio buttons for overall evident
        self.ovlButList = []
        self.overallVar = StringVar()
        self.overallLabel = Label(self.Window, text="overall experience",\
                                   justify=CENTER)
        self.overallLabel.place(relwidth=0.98, relheight=self.smallButtonHeight,\
                relx=0.01, rely=self.ovlStartHeight)
        for each in range(ratingScale):
            x = Radiobutton(self.Window, text=str(each+1),\
                            variable=self.overallVar,\
                        value=str(each+1),tristatevalue=0,\
                            command=self.recordOverallValue)
            x.place(relwidth=self.ratingButtonWidth,relheight=self.smallButtonHeight,\
                    relx=.01+(each*(1/ratingScale)),\
                    rely=self.ovlStartHeight+self.smallButtonHeight+.01)
            self.ovlButList.append(x)

        self.makeTextWindow()

        self.Window.bind("<Escape>",self.closeEvalGui)
        self.Window.mainloop()

    def closeEvalGui(self,event):
        self.videoWindow.destroy()
        self.Window.destroy()

    def getVideoWindowPositions(self):
        # winXpos, winYpos, chatWinWidth, chatWinHeight
        xpos = self.videoWindow.winfo_x()
        ypos = self.videoWindow.winfo_y()
        xwidth = self.videoWindow.winfo_width()
        yheight = self.videoWindow.winfo_height()

        #print(xpos, ypos, xwidth, yheight)
        return xpos, ypos, xwidth, yheight

    def makeTextWindow(self):
        # window for full query and response
        self.textWindow = Toplevel()
        self.textWindow.resizable(width=True, height=True)
        self.textWindow.attributes("-topmost",True)

        geoString = "300x400+10+10" # "200x150+100+100"
        self.textWindow.geometry(geoString)
        self.textWindow.configure(width=300, height=350)

        t =self.data.dataDict[self.currentDataTS]['origQuery']
        self.fullQueryLabel = Label(self.textWindow,\
                                 justify=CENTER, text=t)
        self.fullQueryLabel.place(relwidth=0.98, relheight=0.25, \
                              relx=0.01, rely=0.1)
        self.changeQuery(t)
        
        t = self.data.dataDict[self.currentDataTS]['augResponse']
        if self.randomizeResponse and (self.seeAugResp == False):
            t = self.data.dataDict[self.currentDataTS]['origResponse']

        self.fullResponseLabel = Label(self.textWindow,\
                                 justify=CENTER, text=t)
        self.fullResponseLabel.place(relwidth=0.98, relheight=0.25, \
                              relx=0.01, rely=0.5)
        self.changeResponse(t)

    def makeVideoWindow(self, pathToVideo = None, chatWinWidth = 600, chatWinHeight = 300, \
                        minHeight = 10, ratingScale = 10, winXpos = None, winYpos = None):
        if pathToVideo == None:
            if self.currentVidPath == None:
                # reached end of available data in DATA
                print("out of data... aborting video play...")
                xpos, ypos, xwidth, yheight = self.getVideoWindowPositions()
                self.videoWindow.destroy()
                self.currentVidPath = None
                self.makeVideoWindow(pathToVideo="Video Player",\
                                     chatWinWidth = xwidth, chatWinHeight = yheight, winXpos = xpos, winYpos = ypos)
                return
            pathToVideo = self.currentVidPath
            
        self.videoWindow = Toplevel()
        self.videoWindow.configure(width=chatWinWidth, height=chatWinHeight, bg=self.bgColor)
        blankText = 'loading'
        if pathToVideo == "Video Player":
            blankText = 'Video Player - out of data.'
            
        # center it
        screenWidth = self.videoWindow.winfo_screenwidth()
        screenHeight = self.videoWindow.winfo_screenheight()

        if winXpos == None: # center it (otherwise use positions given)
            winXpos = int((screenWidth-chatWinWidth)/2)
        if winYpos == None:
            winYpos = int(((screenHeight-chatWinHeight)/2)-150)#subtract a little for quick start bar

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
        #self.videoWindow.focus()         
        #self.videoWindow.deiconify()
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
        
    def rePlayVideo(self, remakeVidPath=None):
        self.resetButtons()
        xpos, ypos, xwidth, yheight = self.getVideoWindowPositions()
        self.videoWindow.destroy()
        if remakeVidPath != None:
            self.makeVideoWindow(pathToVideo=remakeVidPath, chatWinWidth = xwidth, \
                                 chatWinHeight = yheight, winXpos = xpos, winYpos = ypos)
        else:
            self.makeVideoWindow(chatWinWidth = xwidth, chatWinHeight = yheight, \
                                 winXpos = xpos, winYpos = ypos)

        #self.makeVideoWindow()
        self.playVideo()
        
    def resetButtons(self):
        for each in self.symButList:
            each.deselect()
        for each in self.appButList:
            each.deselect()
        for each in self.undButList:
            each.deselect()
        for each in self.ovlButList:
            each.deselect()
        print(self.sympathyVar.get(), self.appropriatenessVar.get(), \
              self.understandVar.get(), self.overallVar.get())

    def recordObserverData(self):
        if self.seeAugResp:
            print("used augmented response...")
        else:
            print("used original response...")
        print("recording observer ratings and appending it to: ", self.observerDataPath)
        # timestampStart|+|45||vidPath|+|./test.mp4||origQuery|+|hello||augQuery|+|hello(happy)||origResponse|+|yes?||augResponse|+|you seem happy!\n
        kvDelim = '|+|'
        elDelim = '||'
        ts = str(self.currentDataTS)
        symResp = self.sympathyVar.get()
        appResp = self.appropriatenessVar.get()
        undResp = self.understandVar.get()
        ovlResp = self.overallVar.get()
        
        dataString = 'timestampStart' + kvDelim + ts +\
                     elDelim + 'symResp' + kvDelim + symResp +\
                     elDelim + 'appResp' + kvDelim + appResp +\
                     elDelim + 'undResp' + kvDelim + undResp +\
                     elDelim + 'ovlResp' + kvDelim + ovlResp +\
                     elDelim + 'seeAugResp' + kvDelim + str(self.seeAugResp) + '\n'

        # if file exists, append data to it
        if not os.path.isfile(self.observerDataPath):
            with open(self.observerDataPath,'w') as f:
                f.write(dataString)
        else:
            with open(self.observerDataPath, 'a') as f:
                f.write(dataString)

    def randomizeResp(self):
        if random.randint(1,10) > self.randVal:
            self.seeAugResp = False
        else:
            self.seeAugResp = True

    def nextVideo(self, newVideo = None):
        av = self.appropriatenessVar.get()
        if av=='':
            av=0
        sv = self.sympathyVar.get()
        if sv=='':
            sv=0
        uv = self.understandVar.get()
        if uv=='':
            uv=0
        ov = self.overallVar.get()
        if ov=='':
            ov=0

        if self.cantFindVideo == True or \
           (int(av) > 0 and int(sv) > 0 and int(uv) > 0 and int(ov)):
            print(self.sympathyVar.get(), self.appropriatenessVar.get(),\
                  self.understandVar.get(), self.overallVar.get())
            try:
                if self.outOfData == False and self.cantFindVideo == False:
                    self.recordObserverData()
            except Exception as e:
                print(e)
            #print("New video = ",newVideo,'\n',self.data.dataDict[self.currentDataTS])
            if newVideo == None:
                # find next timestamp and video path
                self.currentDataTS = next(self.dataKeyIter, None)
                if self.randomizeResponse:
                    self.randomizeResp()
                    
                if self.currentDataTS == None:
                    print("reached the end of the data... aborting video playback...")
                    self.outOfData = True
                    xpos, ypos, xwidth, yheight = self.getVideoWindowPositions()
                    self.videoWindow.destroy()
                    self.makeVideoWindow(pathToVideo="Video Player",\
                                 chatWinWidth = xwidth, chatWinHeight = yheight, winXpos = xpos, winYpos = ypos)

                    #self.makeVideoWindow(pathToVideo = 'Video Player')
                    # update buttons
                    self.changeQuery('example query')
                    self.changeResponse('example response')
                else:
                    # set new video playing if all data is present - or skip.
                    try:
                        self.currentVidPath = self.data.dataDict[self.currentDataTS]['vidPath']                           
                        newVideo = self.currentVidPath
                        print("loading: ",newVideo)
                        # update buttons
                        self.changeQuery(self.data.dataDict[self.currentDataTS]['origQuery'])
                        t = self.data.dataDict[self.currentDataTS]['augResponse']
                        if self.randomizeResponse and (self.seeAugResp == False):
                            t = self.data.dataDict[self.currentDataTS]['origResponse']
                        self.changeResponse(t)

                        
                        xpos, ypos, xwidth, yheight = self.getVideoWindowPositions()
                        try:
                            pass # THIS is causing the tkvideo error.............................. not sure why.
                            if self.videoWindow.winfo_exists():
                                #print("The following error is inexplicable but doesn't cause any issues.")
                                self.videoWindow.destroy()
                        except:
                            pass
                        self.currentVidPath = newVideo

                        self.makeVideoWindow(pathToVideo=newVideo,\
                                     chatWinWidth = xwidth, chatWinHeight = yheight, winXpos = xpos, winYpos = ypos)

                        print("nextVideo..........................................")
                    except Exception as e:
                        self.rePlayVideo()
                        print(e)
                        print("problem loading new data... skipping...")
                self.resetButtons() # clear user's choices off radio buttons
        else:
            if self.outOfData != True:
                self.showWarning()

    def showWarning(self, msg = "you must rate the video for all aspects \nbefore moving on to the next video"):
        from tkinter import messagebox
        xpos, ypos, xwidth, yheight = self.getVideoWindowPositions()
        geoString = str(xwidth)+"x"+str('10')+ \
                        "+"+str(xpos)+"+"+str('0')
        self.videoWindow.geometry(geoString)

        eraseMessages = messagebox.showinfo(message=msg, title="WARNING")

        geoString = str(xwidth)+"x"+str(yheight)+ \
                        "+"+str(xpos)+"+"+str(ypos)
        self.videoWindow.geometry(geoString)
        
    def changeQuery(self, newText = "changed"):
        self.queryLabel["text"]=newText
        self.queryLabel.update()

        reformated = self.formatLongText(newText)
        self.fullQueryLabel["text"]="USER QUERY\n\n" + reformated
        self.fullQueryLabel.update()
        
    def changeResponse(self, newText = "changed"):
        self.responseLabel["text"]=newText
        self.responseLabel.update()
        reformated = self.formatLongText(newText)
        self.fullResponseLabel["text"]="CHAT RESPONSE\n\n" + reformated
        self.fullResponseLabel.update()

    def formatLongText(self,t):
        # formats longer queries and responses into 50 letter max wide
        if len(t) > 50:
            temp = ""
            for each in range(int(len(t)/50)+1):
                start = each*50
                stop = (each+1)*50
                if stop > len(t):
                    stop = len(t)
                add = t[start:stop] + "\n"
                temp = temp + add
            return temp
        else:
            return t
        
    def recordSympathyValue(self):
        pass
    def recordAppropriatenessValue(self):
        pass
    def recordUnderstandValue(self):
        pass
    def recordOverallValue(self):
        pass
    
def main():
    evalWin = GUI_EVAL()

if __name__ == "__main__":
    main()
