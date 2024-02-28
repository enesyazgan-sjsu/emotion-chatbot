# emotion-chatbot
SJSU 2024 Grad Project - Emotion Chatbot


#DDAMFN REQUIREMENTS:
Install python 3.8.9: https://www.python.org/downloads/release/python-389/ 
Install pytorch:

# CUDA 11.1
pip install torch==1.8.0+cu111 torchvision==0.9.0+cu111 torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html

# CUDA 10.2
pip install torch==1.8.0 torchvision==0.9.0 torchaudio==0.8.0

# CPU only
pip install torch==1.8.0+cpu torchvision==0.9.0+cpu torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html


Download DDAMFN Repository: https://github.com/simon20010923/DDAMFN
Paste ./networks/ and ./pretrained/ into the main code folder (same folder as main.py)

#To run script:
python main.py


### TO RUN #####

Run VideoStream.py in one terminal. Then, run Gui.py in another terminal.

VideoStream.py creates a server and runs FER on a continuous webcam stream, sending the result of the FER for each captured frame to its client application, gui.py
