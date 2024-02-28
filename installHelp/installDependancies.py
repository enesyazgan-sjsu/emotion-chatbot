import subprocess
import sys
def install(name):
    subprocess.call([sys.executable, '-m', 'pip', 'install', name])

installList = ['opencv-python', 'pillow', 'torch', 'torchvision', 'facenet_pytorch', 'networks']

installList.append('asyncore')
installList.append('networks.DDAM')
installList.append('asynchat')
installList.append('socket')

for each in installList:
	install(each)



