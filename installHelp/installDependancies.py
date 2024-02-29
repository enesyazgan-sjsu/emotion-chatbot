import subprocess
import sys
def install(name):
    subprocess.call([sys.executable, '-m', 'pip', 'install', name])

installList = ['opencv-python', 'pillow', 'torch', 'torchvision', 
	       'facenet_pytorch', 'networks', 'asyncore', 'asynchat',
	      'socket', 'openai', 'python-dotenv']

installList.append('networks.DDAM')

for each in installList:
	install(each)



