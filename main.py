import cv2
import numpy as np
import os  
import sys
import argparse
from PIL import Image

#pytorch libraries
import torch
from torchvision import transforms, datasets
import torch.utils.data as data

##Face Detection Library
from facenet_pytorch import MTCNN

## [FER] DDAMFN Libraries
#obtain fer_model from: https://github.com/simon20010923/DDAMFN
from networks.DDAM import DDAMNet

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raf_path', type=str, default='/data/rafdb/', help='Raf-DB dataset path.')
    parser.add_argument('--batch_size', type=int, default=128, help='Batch size.')
    parser.add_argument('--workers', default=8, type=int, help='Number of data loading workers.')
    parser.add_argument('--num_head', type=int, default=2, help='Number of attention head.')
    parser.add_argument('--model_path', default = './checkpoints/rafdb.pth')
    return parser.parse_args()


def preprocess_webcam_image(image, device, width, height):
    image = Image.fromarray(image)
    data_transforms = transforms.Compose([
        transforms.Resize((width, height)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])]) 
                                 
    image = data_transforms(image)  
    image = image.unsqueeze(0)
    image = image.float()
    image = image.to(device)
    
    
    print(image.size())
    print(type(image))
    print("+++++")
    return image

def capture_and_evaluate_frames(fd_model, fer_model, device, frame_cap = None, width=112, height=112, cam_port=0):
    print("Loading camera. This takes a few seconds..")
    cam = cv2.VideoCapture(cam_port)
    #cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    #cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    print("done loading camera. capturing")
    
    captured_frames = 0
    recording = True
    
    while recording:
        result, frame = cam.read()
        if result:
            captured_frames+=1
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            #extract face from frame with MTCNN
            face = fd_model(frame).permute(1, 2, 0).numpy().astype(np.uint8)

            #make prediction with DDAMFN
            input_tensor = preprocess_webcam_image(face, device, width, height)
            out,feat,heads = fer_model(input_tensor)

            _, prediction = torch.max(out, 1)
            print("Model predicted: " + str(prediction))
            
            if frame_cap is not None and frame_cap <= captured_frames:
                recording = False
    

def main():
    class_names = ['Neutral', 'Happy', 'Sad', 'Surprise', 'Fear', 'Disgust', 'Angry']  

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    #instantiate Face Detection Model
    print("Loading FD Model")
    fd_model = MTCNN(margin=40, select_largest=True, post_process=False)
    fd_model.to(device)
    
    #instantiate FER Model
    print("Loading FER Model")
    args = parse_args()
    fer_model = DDAMNet(num_class=7,num_head=args.num_head)
    fer_model.to(device)
    fer_model.eval() 

    #Running capture/eval loop    
    capture_and_evaluate_frames(fd_model, fer_model, device, frame_cap = 10)
    
    
if __name__ == "__main__":
    main()