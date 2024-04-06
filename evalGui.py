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


PATH_TO_DATA = "./"


# GUI class for evaluation
class GUI_EVAL:
    def __init__(self, chatWinWidth = 400, chatWinHeight = None, minHeight = 10, ratingScale = 10):
        if chatWinHeight == None:
            chatWinHeight = chatWinWidth * .75
        if chatWinHeight <= 0:
            chatWinHeight = minHeight
        chatWinHeight = int(chatWinHeight)
        chatWinWidth = int(chatWinWidth)
        ###################################
        #   BEGIN WINDOW CONSTRUCTION
        ###################################
        self.Window = Tk()
        self.Window.configure(width=chatWinWidth, height=chatWinHeight, bg="#17202A")

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
        #self.Window.state("zoomed") # opens maximized.......
        self.Window.attributes("-topmost",True)
        self.Window.grab_set()
        self.Window.focus()         
        self.Window.deiconify()
        self.Window.title("EVALUATION")
        self.Window.resizable(width=True,
                              height=True)
        # labels
        self.videoLabel = Label(self.Window, text="videoLabel",\
                                justify=CENTER)
        self.videoLabel.place(relwidth=0.98, relheight=0.1, \
                              relx=0.01, rely=0.01)

        self.symStartHeight = 0.24
        # radio buttons for sympathy
        self.sympathyVar = StringVar()
        self.sympathyLabel = Label(self.Window, text="sympathyLabel",\
                                   justify=CENTER)
        self.sympathyLabel.place(relwidth=0.98, relheight=0.1,\
                relx=0.01, rely=self.symStartHeight)
        for each in range(ratingScale):
            x = Radiobutton(self.Window, text=str(each+1),\
                            variable=self.sympathyVar,\
                        value=str(each+1),tristatevalue=0,\
                            command=self.recordSympathyValue)
            x.place(relwidth=1/(ratingScale)-.02,relheight=0.1,\
                    relx=.01+(each*(1/ratingScale)),\
                    rely=self.symStartHeight+0.11)
            
        self.appStartHeight = self.symStartHeight + 0.22
        # radio buttons for appropriateness
        self.appropriatenessVar = StringVar()
        self.appropriatenessLabel = Label(self.Window, text="appropriatenessLabel",\
                                   justify=CENTER)
        self.appropriatenessLabel.place(relwidth=0.98, relheight=0.1,\
                relx=0.01, rely=self.appStartHeight)
        for each in range(ratingScale):
            x = Radiobutton(self.Window, text=str(each+1),\
                            variable=self.appropriatenessVar,\
                        value=str(each+1),tristatevalue=0,\
                            command=self.recordAppropriatenessValue)
            x.place(relwidth=1/(ratingScale)-.02,relheight=0.1,\
                    relx=.01+(each*(1/ratingScale)),\
                    rely=self.appStartHeight+.11)

        self.undStartHeight = self.appStartHeight + 0.22
        # radio buttons for understanding evident
        self.understandVar = StringVar()
        self.appropriatenessLabel = Label(self.Window, text="understandingLabel",\
                                   justify=CENTER)
        self.appropriatenessLabel.place(relwidth=0.98, relheight=0.1,\
                relx=0.01, rely=self.undStartHeight)
        for each in range(ratingScale):
            x = Radiobutton(self.Window, text=str(each+1),\
                            variable=self.understandVar,\
                        value=str(each+1),tristatevalue=0,\
                            command=self.recordUnderstandValue)
            x.place(relwidth=1/(ratingScale)-.02,relheight=0.1,\
                    relx=.01+(each*(1/ratingScale)),\
                    rely=self.undStartHeight+.11)



        self.Window.mainloop()


    def recordSympathyValue(self):
        print(self.sympathyVar.get())
    def recordAppropriatenessValue(self):
        print(self.appropriatenessVar.get())
    def recordUnderstandValue(self):
        print(self.understandVar.get())
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
