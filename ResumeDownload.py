import os
import json
import urllib.request
import threading
from client import *

saveOnAddress = str()
recordsList = list()
completionTracker = dict()
tracker = 0

newFiles = list()
recordsDictForOldFiles = dict()

def seperateFiles(filesToDownload, urls, addressOnDisk):

	saveOnAddress = addressOnDisk

	print(filesToDownload)

	for file in filesToDownload:
		if (file + " Record.json") in os.listdir(addressOnDisk):
			with open(file+" Record.json") as fin:
				recordDictionary = json.load(fin)
			print("Resuming", file)
			recordsDictForOldFiles[file] = (recordDictionary, urls[file])
			makeThreadsToResumeFiles(recordsDictForOldFiles)
			remakeThreads(file, urls[file], recordDictionary)

		else:
			print("File", file, "is not present in the directory. Download will start over!") 


def makeThreadsToResumeFiles(dictionaryForOldFiles):
	for file in dictionaryForOldFiles:
		fileThread = threading.Thread(target=remakeThreads, args(file, dictionaryForOldFiles[1], dictionaryForOldFiles[0]))
		fileThread.start()

def remakeThreads(fileName, link, bytesRecord):
	
	global tracker

	completionTracker[tracker] = 0
	recordsList.append(dict())
	
	for i in bytesRecord:
		downloadedByteRange = bytesRecord[i]
		totalFileSize = getFileSize(link)
		sizeForEachThread = totalFileSize/len(bytesRecord)
		byteRange = (bytesRecord[i][1]+1, int(sizeForEachThread*(int(i)+1))-1)
		resumeDownloadThread = threading.Thread(target=resumeDownload, args=(fileName, link, byteRange,tracker, i, len(bytesRecord)))
		resumeDownloadThread.start()

	tracker += 1


def resumeDownload(fileName, link, byteRange, fileNum, threadNum, numberOfOldThreads):

	countBytes = byteRange[0]
	increment = 51199

	while countBytes <= byteRange[1]:

		req = urllib.request.Request(link)
		bytesToDownload = 'bytes=%s-%s' % (countBytes, countBytes+increment)
		req.add_header("Range", bytesToDownload)
		f = urllib.request.urlopen(req)

		with open(saveOnAddress+threadNum+fileName, "ab") as output:
			output.write(f.read())

		print("Bytes done:", bytesToDownload)
		print("RecordsList: ", recordsList)
		print("File Number: ", fileNum)
		print("Thread Number: ", threadNum)

		recordsList[fileNum][threadNum] = (byteRange[0], countBytes+increment)
		print("Bytes done:", (byteRange[0], countBytes+increment))

		with open(saveOnAddress+fileName+" Record.json", "w") as record:
			record.write(json.dumps(recordsList[fileNum]))

		countBytes += 51200

		if(countBytes+51199) > byteRange[1]: increment = byteRange[1]-countBytes

	completionTracker[fileNum] += 1
	if(completionTracker[fileNum] == numberOfOldThreads): finishDownload(fileName, numberOfOldThreads) 



def finishDownload(fileName, numberOfOldThreads):
	for i in range(numberOfOldThreads):
		with open(str(i)+fileName, "rb") as aFile:
			data = aFile.read()
		with open(fileName, "ab") as com:
			com.write(data)
	deleteExistingParts(fileName, numberOfOldThreads)


def deleteExistingParts(fileName, numberOfOldThreads):
	for i in range(numberOfOldThreads):
		os.remove(str(i)+fileName)
	os.remove(fileName + " Record.json")


def getFileSize(url):
	data = urllib.request.urlopen(url)
	return float(data.info()['Content-Length'])







