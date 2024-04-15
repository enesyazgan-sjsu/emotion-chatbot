from dataHandler import DATA

x = DATA()
x.readData('./eric_0/tempDataSave.txt')
counter = 0
for each in x.dataDict.keys():
    counter+=1
    print(counter)
    print(each)
    tempAug = x.dataDict[each]['augQuery']
    tempAug = tempAug.split(')')[0] # (Reply as if you see that I have a Neutral facial expression.
    tempAug = tempAug.split(' a ')[1]
    tempAug = tempAug.split(' facial')[0]
    print(tempAug)
    print()
    
