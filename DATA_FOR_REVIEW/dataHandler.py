
# DATA class for video, queries, timestamps, responses
class DATA:
    def __init__(self, path = None):
        self.dataDict = {} # timestampStart is the integer part of the time start 
        # {"timestampStart" : {'vidPath'   : "",\
        #                      'origQuery' : "",\
        #                      'augQuery'  : "",\
        #                      'origResponse' : "",\
        #                      'augResponse'  : ""} }
        self.delimElement = '||'
        self.delimKeyVal = '|+|'
        if path != None:
            self.readData(path)
        self.averageSimilarity = None
        
    def addData(self, ts, vp, oq, aq, orr, ar):
        self.dataDict[ts] = {'vidPath' : vp, 'origQuery' : oq,\
                             'augQuery' : aq, 'origResponse' : orr,\
                             'augResponse' : ar}
    def printData(self, ts = None):
        if ts == None:
            for each in self.dataDict.keys():
                print(each, self.dataDict[each])
        else:
            print(self.dataDict[ts])
    def removeData(self, ts):
        del self.dataDict[ts]
    def saveData(self, savePath = './__testDataSave.txt'):
        # saves new complete file (overwrites file)
        with open(savePath, "w") as f:
            for timestamp in self.dataDict.keys():
                stringToWrite = "timestampStart" + self.delimKeyVal + timestamp
                for element in self.dataDict[timestamp].keys():
                    temp = self.dataDict[timestamp][element]
                    temp = temp.replace('\n','\\n')
                    temp = temp.replace('\\n\\n','\\n')
                    stringToWrite = stringToWrite + self.delimElement + element
                    stringToWrite = stringToWrite + self.delimKeyVal + temp
                stringToWrite = stringToWrite+'\n'
                f.write(stringToWrite)
    def readData(self, readPath = './__testDataSave.txt'):
        # reads complete file in (overwrites memory)
        self.dataDict = {}
        with open(readPath, 'r') as f:
            for line in f:
                tempDict = {}
                for keyVal in line.split(self.delimElement):
                    kv = keyVal.split(self.delimKeyVal)
                    if kv[0] == 'timestampStart':
                        ts = kv[1]
                    else:
                        tempDict[kv[0]]=kv[1]
                self.dataDict[ts]=tempDict
    def getNext(self):
        return
    
