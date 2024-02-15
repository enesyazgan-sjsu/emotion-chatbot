# importing OpenCV library
import cv2
import numpy as np
import os  
import time

def capture_database_frames(data_dir, num_frames_to_capture, category_maximum, target_resolution = (256,256), delay_s = 0.05, ext = ".png", name_length = 5, cam_port = 0):
    print("loading camera. This takes a few seconds..")
    cam = cv2.VideoCapture(cam_port)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("done loading camera. capturing")
    
    #check number of frames in data_folder already
    num_prexisiting_frames = len(list(os.listdir(data_dir)))
    
    frame_num = num_prexisiting_frames
    captured_frames = 0
    capturing = True
    
    start_time = time.time()
    while capturing:
        if captured_frames + num_prexisiting_frames >= category_maximum:
            print("Reached category limit of: " + str(category_maximum) + " images. Terminating capture.")
            capturing = False
        
        if captured_frames >= num_frames_to_capture:
            print("Captured: " + str(num_frames_to_capture))
            capturing = False

        capture_time = time.time()
        if capture_time - start_time > delay_s:
            start_time = time.time()
            print("Capturing image: " + str(frame_num))
            result, image = cam.read()
            if result and capturing:
                captured_frames+=1
                
                image = cv2.resize(image, target_resolution, interpolation = cv2.INTER_AREA)
                
                frame_str = str(frame_num)
                image_name = "0"*(name_length-len(frame_str)) + frame_str+ext
                
                cv2.imwrite(data_dir+image_name, image)
                frame_num+=1


def mkdir_if_dne(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

def main():
    main_dataset_folder = "./emotion_dataset/"
    mkdir_if_dne(main_dataset_folder)
    
    emotion = "happy"
    emotion_subfolder = main_dataset_folder + emotion + "/"
    mkdir_if_dne(emotion_subfolder)
    
    
    category_maximum = 300
    num_frames_to_capture = 128
    target_resolution = (256,256)
    delay_between_frames_s = 0.05 #capture delay in seconds
    
    print("You are about to capture " + str(num_frames_to_capture) + " images.")
    print("Make sure to appear: " + str(emotion))
    print("Get ready!")
    
    capture_database_frames(emotion_subfolder, num_frames_to_capture, category_maximum, target_resolution = target_resolution, delay_s = delay_between_frames_s)
    
    
if __name__ == "__main__":
    main()