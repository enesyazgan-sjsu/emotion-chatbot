import cv2
import numpy as np
import os  
import sys
import argparse

##DDAMFN Libraries
import torch
from torchvision import transforms, datasets
import torch.utils.data as data
from networks.DDAM import DDAMNet

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raf_path', type=str, default='/data/rafdb/', help='Raf-DB dataset path.')
    parser.add_argument('--batch_size', type=int, default=128, help='Batch size.')
    parser.add_argument('--workers', default=8, type=int, help='Number of data loading workers.')
    parser.add_argument('--num_head', type=int, default=2, help='Number of attention head.')
    parser.add_argument('--model_path', default = './checkpoints/rafdb.pth')
    return parser.parse_args()

def capture_and_evaluate_frames(model, frame_cap = None, width=224, height=224, cam_port=0):
    print("loading camera. This takes a few seconds..")
    cam = cv2.VideoCapture(cam_port)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    print("done loading camera. capturing")
    
    captured_frames = 0
    
    recording = True
    
    while recording:
        result, image = cam.read()
        if result:
            captured_frames+=1
            image = cv2.resize(image, (width,height), interpolation = cv2.INTER_AREA)
            image = np.expand_dims(image, axis=0)
            
            #make prediction with DDAMFN
            
            tensor = torch.from_numpy(image)
            prediction = model(tensor)
            print("Model predicted: " + str(prediction))
            
            if frame_cap is not None and frame_cap <= captured_frames:
                recording = False
    

def main():
    class_names = ['Neutral', 'Happy', 'Sad', 'Surprise', 'Fear', 'Disgust', 'Angry']  

    #obtain model from: https://github.com/simon20010923/DDAMFN
    model_folder = "./DDAMFN-main/DDAMFN-main/pretrained/"
    model_name = "MFN_msceleb.pth"
    
    args = parse_args()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = DDAMNet(num_class=7,num_head=args.num_head)
    model.to(device)
    model.eval()   
    
    capture_and_evaluate_frames(model, frame_cap = 10)
    
    
if __name__ == "__main__":
    main()