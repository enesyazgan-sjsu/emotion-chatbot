import os
from openai import OpenAI

'''
# class to handle chatGPT messaging
# example use:
x = ChatHandler()
x.initializeAPI()
x.sendMessage()
print(x.returnReply())
'''

class ChatHandler:
    def __init__(self):
        self.message = 'Say this is a test.'
        self.role = 'user'
        self.model = 'gpt-3.5-turbo'
        self.api_key = ''
        self.client = None
        self.chatCompletion = None
        self.reply = None
        
    def initializeAPI(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key = self.api_key)
        self.api_key = '' # deleted for security concerns

    def defineMessage(self, message='Say this is a test.'):
        self.message = {"role":self.role, "content":self.message}
    def defineRole(self, role='user'):
        self.role = role
    def defineModel(self, model = 'gpt-3.5-turbo'):
        self.model = model

    def sendMessage(self):
        self.chatCompletion = self.client.chat.completions.create(messages=[{"role":"user","content":"Say this is a test"}],
                                                                  model="gpt-3.5-turbo")
        return (self.chatCompletion)
    def returnReply(self):
        return(self.chatCompletion.choices[0].message.content)

