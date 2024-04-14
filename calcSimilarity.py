from dataHandler import DATA
import os, sys, subprocess

from sentence_transformers import util, SentenceTransformer

class calcSimilarity:
    def __init__(self, dataPath = './tempDataSave.txt',\
                 outputPath = './dataWithSim.txt',\
                 kvDelim = '|+|',\
                 elDelim = '||',\
                 saveData = True, showProgress = True):

        if showProgress:
            print(".",end='')
        self.x = DATA(dataPath)
        if showProgress:
            print(".",end='')
        self.average = 0.0
        if showProgress:
            print(".",end='')

        # Load the model
        model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')

        if showProgress:
            print(".",end='')
        for each in self.x.dataDict.keys():
            if showProgress:
                print(".",end='')
            # compute semantic similarity between origResponse and augResponse
            # Encode the paragraphs
            try:
                origResp = self.x.dataDict[each]['origResponse']
                augResp = self.x.dataDict[each]['augResponse']
                if showProgress:
                    print(".",end='')
                origRespEmbed = model.encode(origResp)
                if showProgress:
                    print(".",end='')
                augRespEmbed = model.encode(augResp)
                if showProgress:
                    print(".",end='')
            except Exception as e:
                print(e)
                print("problem embedding responses...")
                
            # Calculate the cosine similarity
            if showProgress:
                print(".",end='')
            semSim = util.cos_sim(origRespEmbed, augRespEmbed)
            if showProgress:
                print(".",end='')
            semSim = float((str(semSim[0][0]).split("(")[1][:-1]))
            if showProgress:
                print(".",end='')
            # add to dataDict
            self.x.dataDict[each]['semSim']=str(semSim)
            if showProgress:
                print(".",end='')

        self.calcAverage()

        if showProgress:
            print(".",end='')
        if saveData:
            self.x.saveData(outputPath)

    def calcAverage(self):
        totNum = 0
        totSim = 0.0
        for each in self.x.dataDict.keys():
            try:
                totSim = totSim + float(self.x.dataDict[each]['semSim'])
                totNum +=1
            except Exception as e:
                print(e)
                print("problem with ",each,"skipping...")
        self.average = totSim / totNum
        self.x.averageSimilarity = self.average


sim = calcSimilarity()
print("\nsimilarity average = ", sim.x.averageSimilarity)
#print("\nsimilarity average = ", sim.average)
#print(sim.x.dataDict)
