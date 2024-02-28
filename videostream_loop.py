import cv2
import numpy as np
import os  
import sys
import argparse
from PIL import Image as Img

#pytorch libraries
import torch
from torchvision import transforms, datasets
import torch.utils.data as data

##Face Detection Library
from facenet_pytorch import MTCNN

## [FER] DDAMFN Libraries
#obtain fer_model from: https://github.com/simon20010923/DDAMFN
from networks.DDAM import DDAMNet

##networking libraries
import asyncore, asynchat, socket

# GUI implemented using: https://www.geeksforgeeks.org/gui-chat-application-using-tkinter-in-python/
from tkinter import *

########################################
##### SERVER COMMUNICATION MODULES #####
########################################

class MainServerSocket(asyncore.dispatcher):
    def __init__(self, port, fd_model, fer_model, device):
        ## FER vars ###
        self.fd_model = fd_model
        self.fer_model = fer_model
        self.device = device
    
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('',port))
        self.port = port
        self.listen(5)
        
    def handle_accept(self):
        newSocket, address = self.accept()
        newSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Connected from: " + str(address))
        
        fer_server = FERServer(self.fd_model, self.fer_model, self.device, newSocket)
        
class FERServer(asynchat.async_chat):
    def __init__(self, fd_model, fer_model, device, *args):
        ## FER vars ###
        self.fd_model = fd_model
        self.fer_model = fer_model
        self.device = device
    
        asynchat.async_chat.__init__(self, *args)
        self.terminator = "#"
        self.set_terminator(self.terminator)
        
        self.run_fer_loop(frame_cap=None)
    
    def preprocess_webcam_image(self, image, width, height):
        image = Img.fromarray(image)
        data_transforms = transforms.Compose([
            transforms.Resize((width, height)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])]) 
                                     
        image = data_transforms(image)  
        image = image.unsqueeze(0)
        image = image.float()
        image = image.to(self.device)
        return image
    
    def run_fer_loop(self, frame_cap = None, width=112, height=112, cam_port=0):
        class_names = ['Neutral', 'Happy', 'Sad', 'Surprise', 'Fear', 'Disgust', 'Angry'] 
        
        print("Loading camera. This takes a few seconds..")
        cam = cv2.VideoCapture(cam_port, cv2.CAP_DSHOW)
        print("done loading camera. capturing")
        
        captured_frames = 0
        recording = True
        
        while recording:
            result, frame = cam.read()
            if result:
                captured_frames+=1
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                #extract face from frame with MTCNN
                face = self.fd_model(frame)
                if face is not None:
                    face = face.permute(1, 2, 0).numpy().astype(np.uint8)

                    #make prediction with DDAMFN
                    input_tensor = self.preprocess_webcam_image(face, width, height)
                    out,feat,heads = self.fer_model(input_tensor)

                    _, prediction = torch.max(out, 1)
                    message = str(class_names[prediction[0].tolist()])+self.get_terminator()
                else:
                    prediction = -1
                    message = str("None")+self.get_terminator()
                    
                #send FER Result to Client
                print("sending: " + message) #delete soon
                self.push(message.encode("utf-8"))
                    
                if frame_cap is not None and frame_cap <= captured_frames:
                    recording = False
        
    def handle_close(self):
        self.close()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raf_path', type=str, default='/data/rafdb/', help='Raf-DB dataset path.')
    parser.add_argument('--batch_size', type=int, default=128, help='Batch size.')
    parser.add_argument('--workers', default=8, type=int, help='Number of data loading workers.')
    parser.add_argument('--num_head', type=int, default=2, help='Number of attention head.')
    parser.add_argument('--model_path', default = './checkpoints/rafdb.pth')
    return parser.parse_args()

def main():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    #instantiate Face Detection Model
    print("Loading FD Model")
    if device.type == 'cuda':
        fd_model = MTCNN(margin=40, select_largest=True, post_process=False, device = "cuda")
    else:
        fd_model = MTCNN(margin=40, select_largest=True, post_process=False)
    fd_model.to(device)
    
    #instantiate FER Model
    print("Loading FER Model")
    args = parse_args()
    fer_model = DDAMNet(num_class=7,num_head=args.num_head)
    fer_model.to(device)
    fer_model.eval() 

    print("Starting FER Server")
    #instantiate FER Reciever Server
    port = 400
    fer_server = MainServerSocket(port, fd_model, fer_model, device)
    asyncore.loop()

    
if __name__ == "__main__":
    main()
