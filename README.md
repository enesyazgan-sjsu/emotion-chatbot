# emotion-chatbot
SJSU 2024 Grad Project - Emotion Chatbot

# You will need your own OPENAI_API_KEY
Become a member and get a key. Instructions at top of gui.py

Best practices as per OpenAI is to set an environment variable:

https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety



#DDAMFN REQUIREMENTS:
Install python 3.8.9: https://www.python.org/downloads/release/python-389/ 
Install pytorch:

# CUDA 11.1
pip install torch==1.8.0+cu111 torchvision==0.9.0+cu111 torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html

# CUDA 10.2
pip install torch==1.8.0 torchvision==0.9.0 torchaudio==0.8.0

# CPU only
pip install torch==1.8.0+cpu torchvision==0.9.0+cpu torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html

************************
**RUNNING INSTRUCTIONS**
************************
Download DDAMFN Repository: https://github.com/simon20010923/DDAMFN
(copy of necessary folders provided in installHelp folder)

Paste ./networks/ and ./pretrained/ into the main code folder (same folder as main.py)

run installDependancies.py -- this should install any necessary modules on your system.

### TO RUN THE GUI ALONE ####
set useServer to False at top of gui.py

### TO RUN THE GUI AND WEBCAM SERVER #####

Run VideoStream.py in one terminal. Then, run Gui.py in another terminal.

VideoStream.py creates a server and runs FER on a continuous webcam stream, sending the result of the FER for each captured frame to its client application, gui.py

### If you have trouble installing dependancies for DoSpeech.py ###
Uncomment the code at the top of DoSpeech.py for initial run, it will 
install dependancies on your system for you. (then you can re-comment it out 
because it takes a long time)
#######################################
## FUNCTIONS
#######################################

3/1/24:
**SYSTEM COMMANDS**
Using a command prefix, you can change and print variables during the chat to test different situations without restarting the system. For example:

%%% self.showAugmentation False

will cause the client to stop showing the user the emotional augmentation (although it still sends it to chatGPT)

%%% print self.useAugmentation

will output the status of the self.useAugmentation variable

self.commandList is a list of supported variables (we could change it to just expose all variables easily).

**GUI NAVIGATION**
entering an api-key in the first window will use that - otherwise it will look for an environment variable to use

shift-enter will send the text to chatGPT (as will the send button)
