# import dependancies
import subprocess
import sys
def install(name):
    subprocess.call([sys.executable, '-m', 'pip', 'install', name])

install('SpeechRecognition')
install('libasound2-dev')
install('portaudio19-dev')
install('libportaudio2')
install('libportaudiocpp0')
install('ffmpeg')
install('pyaudio')
# you may need to do this:
# apt install libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg
# pip install pyaudio

#------------------------------

import speech_recognition as sr
import time
from os import path

class DoSpeech:
    
    # class to handle speech recognition by voice or file
    def __init__(self, __file__ = "", timeSlices = [],
                 service = "Google_Speech_Recognition", verbose = True):
        from os import path
        
        self.AUDIO_FILE = __file__
        self.verbose = verbose
        # list of time slices to process in milliseconds from beginning
        # processes whole input if empty
        self.timeSlices = timeSlices # [ [1560, 2560], ... ] 
        self.service = service
        self.r = sr.Recognizer()
        self.output = []
        self.outputDict = []
        
    def msTime(self): # return current time in seconds
        return round(time.time() * 1000)

    def printMicrophoneDevices(self): # prints device numbers
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))


    def recSpeech(self, audio, service,start= None, end=None):
        # recognize speech in audio using service (internal function)
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            if service == 'Google_Speech_Recognition':
                self.outputDict.append(self.r.recognize_google(audio, show_all = True))
                self.output.append([self.r.recognize_google(audio),start,end])
                if self.verbose:
                    print(f"{service} thinks you said:\n " + self.output[-1][0])
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    
        
    def recognizeSpeechFromFile(self, file, timeSlices = [[None,None]]):
        # process audio file from start to end point in seconds -->> [ [None, 5.0]...]
        self.AUDIO_FILE = file
        print("using: ", self.AUDIO_FILE)
        for each in timeSlices:
            print(f"processing {each} time slice...")
            start = each[0]
            end = each[1]
            with sr.AudioFile(self.AUDIO_FILE) as source:
                if start == None and end == None:
                    audio = self.r.record(source) # read entire file
                elif end == None:
                    audio = self.r.record(source, offset = start) # read to the end
                else:
                    audio = self.r.record(source, offset = start, duration = end-start) # read slice

            if self.verbose:
                print(self.msTime())
            self.recSpeech(audio, self.service,start,end)
            if self.verbose:
                print(self.msTime())
            print()
        print()

    def recognizeSpeechFromMic(self):
        # process microphone input
        # obtain audio from the microphone
        # sr.Microphone(device_index=0) for specific device (find index above)
        with sr.Microphone() as source:
            print("Say something!")
            audio = self.r.listen(source)

        if self.verbose:
            print(self.msTime())
        self.recSpeech(audio, self.service)
        if self.verbose:
            print(self.msTime())
        print()



y = DoSpeech()
y.recognizeSpeechFromFile("./harvard.wav",timeSlices=[[1.6, 3.987664],[None,None]])
#y.recognizeSpeechFromMic()
print(y.output)
print()
#print(y.outputDict)
#y.recognizeSpeechFromMic()
#print(y.output)
