import threading
import urllib.request
import json
from CommonFunctions import * 
from SingleConnectionDownloading import *


def downloadfile(link, byteRange, fileName, fileNum, threadNum):

	byteRange = (int(byteRange[0]), int(byteRange[1]))

	countBytes = byteRange[0]
	increment = 51199

	while countBytes <= byteRange[1]:

		req = urllib.request.Request(link)
		bytesToDownload = 'bytes=%s-%s' % (countBytes, countBytes+increment)
		req.add_header('Range', bytesToDownload)
		f = urllib.request.urlopen(req)

		with open(storeAddress+fileName, 'ab') as output:
			output.write(f.read())

		listOfRecords[fileNum][threadNum] = (byteRange[0], countBytes+increment)

		with open(storeAddress+fileName[1:]+" Record.json", "w") as record:
			record.write(json.dumps(listOfRecords[fileNum]))

		countBytes += 51200

		if (countBytes+51199) > byteRange[1]: increment = byteRange[1]-countBytes

	mergeDictionary[fileNum] += 1
	if mergeDictionary[fileNum] == numOfSimulConn: 
		downloadComplete(fileName[1:], numOfSimulConn)
	
		
def createNewDownloadThread(link, byteRange, fileName, fileNum, threadNum):
    download_thread = threading.Thread(target=downloadfile, args=(link, byteRange, fileName, fileNum, threadNum))
    download_thread.start()


def startMakingConnections(numOfThreads, fileName, fileAddress, sizeForEachThread, fileNum):

	for i in range(numOfThreads):
		#print(i)
		createNewDownloadThread(fileAddress, (i*sizeForEachThread, ((i+1)*sizeForEachThread-1)), str(i)+fileName, fileNum, i)


def processThreadsForFiles(file, fileName, fileNum, simulConn, sA):
	

	global numOfSimulConn
	global storeAddress

	
	numOfSimulConn = simulConn
	storeAddress = sA

	if acceptsByteRange(file):
		listOfRecords.append(dict())
		fileSize = getFileSize(file)
		#print("File Size:", fileSize)
		sizeForEachThread = fileSize/numOfSimulConn
		#print("Size for each thread:", sizeForEachThread)
		mergeDictionary[fileNum] = 0
		startMakingConnections(numOfSimulConn, fileName, file, sizeForEachThread, fileNum)

	else:
		print("File stored on", storeAddress)
		print("\n\n\nDownloading\n\n\n", fileName)
		completeFileDownload = threading.Thread(target=downloadWholeFile, args=(file, storeAddress+fileName))
		completeFileDownload.start()


listOfRecords = list()
mergeDictionary = dict()
numOfSimulConn, number, storeAddress = 0, 0, ""