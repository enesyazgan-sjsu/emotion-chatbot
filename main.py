import tensorflow as tf
from tensorflow import keras
# importing OpenCV library
import cv2
import numpy as np
import os  


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
            prediction = model.evaluate(image) 
            print("Model predicted: " + str(prediction))
            
            if frame_cap is not None and frame_cap <= captured_frames:
                recording = False
    

def main():
    print("Running TF Version: " + str(tf.__version__))
    model_folder = "./PAtt-Lite-main/PAtt-Lite-main/pretrained/"
    model_name = "rafdb.h5"
    
    patt_lite = keras.models.load_model(model_folder+model_name)
    
    capture_and_evaluate_frames(patt_lite, frame_cap = 10)
    
    
if __name__ == "__main__":
    main()