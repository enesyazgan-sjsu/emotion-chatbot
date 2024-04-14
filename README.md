# emotion-chatbot
SJSU 2024 Grad Project - Emotion Chatbot

## Summary
- This system allows a user to communicate with a chatbot that has been enhanced with awareness of the user's emotions. It captures facial expressions, classifies their emotions, and augments user questions with the predicted emotion. This information is used to provide more relevant and sympathetic responses from the chatbot.

************************************
# **Instructions: First-time Setup**
************************************

## Clone repo:
`git clone https://github.com/enesyazgan-sjsu/emotion-chatbot.git`

## Install python 3.8.9: 
- https://www.python.org/downloads/release/python-389/

### Windows-specific Instructions
- Update your path to include Python 3.8.9
- Should look like: C:\Users\<your Windows profile name>\AppData\Local\Programs\Python\Python38
- Make sure to set it to the highest priority, so it doesn't get overwritten by default Windows store trigger
- Restart VS Code (not just terminal) for change to take effect
- Typing `python`, in a command prompt, will confirm whether you are setup, correctly

## Install pytorch:

### CUDA 11.1
`pip install torch==1.8.0+cu111 torchvision==0.9.0+cu111 torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html`

### CUDA 10.2
`pip install torch==1.8.0 torchvision==0.9.0 torchaudio==0.8.0`

### CPU only
`pip install torch==1.8.0+cpu torchvision==0.9.0+cpu torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html`

## OpenAI API Key
- This project utilizes Open AI's ChatGPT. You will need to create a free account and generate your own API key.
- Navigate to your API Key page: https://platform.openai.com/api-keys
- Create a new key and paste it somewhere safe (Open AI will never allow you to see it again)
- Set the environment variable OPENAI_API_KEY: <your API key>
- Best practices as per OpenAI is to set an environment variable: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety

## Install other Python dependencies
`pip install -r requirements.txt`
or run installDependancies.py in the installHelp folder if you are still having problems.

## POTENTIAL ISSUE **********************************************
If networks.DDAM is not being found correctly, you may have to rename a folder called 'networks' to something else, like 'networks_OLD'. 
This should fix the issue (that networks is being found before the networks folder local to this repository.
The 'networks' folder should be here:
    C:\Users\YOUR_USERNAME\AppData\Local\Python\Python310\site-packages
          or potentially here if you are on a roaming profile:
    C:\Users\YOUR_USERNAME\AppData\Roaming\Python\Python310\site-packages
Also, AppData may be hidden from view by default. Choose View->HiddenItems from your file browser window.

### Helpful Tips
- If you have trouble constantly installing dependancies for DoSpeech.py, then uncomment the code at the top of DoSpeech.py for the initial run. It will install dependancies on your system for you. Then, you can re-comment it out, afterwards, because it takes a long time.

**************************
# **Instructions: How to Run**
**************************

## User interface
- `python gui.py` will start the GUI client and attempt to launch the backend server


## Evaluation (observers) interface
- `python evalGui.py` will start the evaluation software reading tempDataSave.txt and dataFolder/* for saved (from gui sessions) data
- and it will output observer ratings to observerData.txt

## Calculate the semantic similarity of saved data
- `python calcSimilarity.py` will read in tempDataSave.txt, calculate semantic similarity between original response and augmented response
- and output to dataWithSim.txt
  
### Helpful Tips
- If this fails, then change `useAutoSpawn = False`, at the top of gui.py, run `python videostream_loop.py` in one terminal, and `python gui.py` in another (after)
- To run only the GUI (without webcam server), set `useServer = False`, at top of gui.py
- videostream_loop.py starts the backend server which runs the continuous webcam capture loop, sends the cropped images to the FER model, then appends the user queries and predicted emotion to ChatGPT.

### If you have trouble installing dependancies for DoSpeech.py ###
Uncomment the code at the top of DoSpeech.py for initial run, it will 
install dependancies on your system for you. (then you can re-comment it out 
because it takes a long time)

#######################################
# **Instructions: GUI Functions**
#######################################

3/1/24:

## **SYSTEM COMMANDS**
Using a command prefix, you can change and print variables during the chat to test different situations without restarting the system. For example:

%%% self.showAugmentation False

will cause the client to stop showing the user the emotional augmentation (although it still sends it to chatGPT)

%%% print self.useAugmentation

will output the status of the self.useAugmentation variable

%%% help

will output self.commandList which is a list of supported variables, but currently any variable will work if you know what it is...

## **GUI NAVIGATION**

The system will look for an api-key on your system, failing that, it will warn you and you can enter an api-key in the first window (login). It will attempt to set that key on your system so you can skip it the next time.

shift-enter will send the text to chatGPT (as will the send button)

3/10/24:

## **multiple EAR**
self.useMultEAR = True (current default) will cause the system to add emotional augmentation at multiple points within a single chat input. False will only use one emotional augmentation.

#######################################
# **Credits: Contributers**
#######################################
- Gurpeet Grewal
- Eric Mead
- Brandon Winn
- Enes Yazgan
