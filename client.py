import sys
import json
import os
import threading
import urllib.request
from ResumeDownload import *
from CommonFunctions import *
from SingleConnectionDownloading import *

def parseArguments():

	parameters = sys.argv[1 : ]

	resumeDownload = "-r" in parameters

	numOfSimultaneousConn = int(parameters[parameters.index("-n") + 1])
	interval = float(parameters[parameters.index("-i") + 1])
	numOfFilesToDownload = int(parameters[parameters.index("-nf") + 1])
	SaveOnAddress = str(parameters[parameters.index("-o") + 1])

	filesAddresses = list()

	for i in range(0, numOfFilesToDownload):
		filesAddresses.append(str(parameters[parameters.index("-f") + i+1]))

	return resumeDownload, numOfSimultaneousConn, interval, numOfFilesToDownload, SaveOnAddress, filesAddresses


def downloadfile(link, byteRange, fileName, fileNum, threadNum):

	byteRange = (int(byteRange[0]), int(byteRange[1]))

	countBytes = byteRange[0]
	increment = 51199

	while countBytes <= byteRange[1]:

		req = urllib.request.Request(link)
		bytesToDownload = 'bytes=%s-%s' % (countBytes, countBytes+increment)
		req.add_header('Range', bytesToDownload)
		f = urllib.request.urlopen(req)

		with open(sA+fileName, 'ab') as output:
			output.write(f.read())

		listOfRecords[fileNum][threadNum] = (byteRange[0], countBytes+increment)

		with open(sA+fileName[1:]+" Record.json", "w") as record:
			record.write(json.dumps(listOfRecords[fileNum]))

		countBytes += 51200

		if (countBytes+51199) > byteRange[1]: increment = byteRange[1]-countBytes

	mergeDictionary[fileNum] += 1
	if mergeDictionary[fileNum] == simulConn: 
		downloadComplete(fileName[1:], simulConn)
	
		

def createNewDownloadThread(link, byteRange, fileName, fileNum, threadNum):
    download_thread = threading.Thread(target=downloadfile, args=(link, byteRange, fileName, fileNum, threadNum))
    download_thread.start()


def startMakingConnections(numOfThreads, fileName, fileAddress, sizeForEachThread, fileNum):

	for i in range(numOfThreads):
		#print(i)
		createNewDownloadThread(fileAddress, (i*sizeForEachThread, ((i+1)*sizeForEachThread-1)), str(i)+fileName, fileNum, i)


def processThreadsForFiles(file, fileName, fileNum):
	
	if acceptsByteRange(file):
		global no
		listOfRecords.append(dict())
		fileSize = getFileSize(file)
		#print("File Size:", fileSize)
		sizeForEachThread = fileSize/simulConn
		#print("Size for each thread:", sizeForEachThread)
		mergeDictionary[fileNum] = 0
		startMakingConnections(simulConn, fileName, file, sizeForEachThread, fileNum)
		no += 1 

	else:
		print("File stored on", sA)
		print("\n\n\nDownloading\n\n\n", fileName)
		completeFileDownload = threading.Thread(target=downloadWholeFile, args=(file, sA+fileName))
		completeFileDownload.start()


def startNewFiles(newFiles):
	global no
	for file in newFiles:
		fileName = file[file.rfind("/")+1 : ]
		fileThread = threading.Thread(target=processThreadsForFiles, args=(file, fileName, no))
		fileThread.start()
		no += 1

resumeDownload, simulConn, interval, fTD, sA, fA = parseArguments()

no = 0
listOfRecords = list()
files = list()
mergeDictionary = dict()
filesAndUrls = dict()

#print(resumeDownload)
#print("Number of simultaneous connection:", simulConn)
#print("Interval", interval)
#print("Number of files to download:", fTD)
#print("Files will be saved on", sA )
#print("Files will be downloaded from:", fA)

for file in fA:
	
	fileName = file[file.rfind("/")+1 : ]
	files.append(fileName)
	filesAndUrls[fileName] = file
	
if resumeDownload:
	newFiles = seperateFiles(files,filesAndUrls, sA)
	startNewFiles(newFiles)