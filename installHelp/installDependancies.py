import subprocess
import sys
def install(name):
    subprocess.call([sys.executable, '-m', 'pip', 'install', name])

installList = ['opencv-python', 'pillow', 'torch', 'torchvision', 
	       'facenet_pytorch', 'networks', 'asyncore', 'asynchat',
	      'socket', 'openai']

installList.extend(['SpeechRecognition','libasound2-dev', 'portaudio19-dev',
                'libportaudio2', 'libportaudiocpp0', 'ffmpeg', 'pyaudio', 'tkvideo'])

for each in installList:
	install(each)



