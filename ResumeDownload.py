import os
import json
import urllib.request
import threading
from CommonFunctions import *

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
			
			#remakeThreads(file, urls[file], recordDictionary)

		else:
			newFiles.append(urls[file])

	makeThreadsToResumeFiles(recordsDictForOldFiles)

	return newFiles


def makeThreadsToResumeFiles(dictionaryForOldFiles):

	global tracker

	for file in dictionaryForOldFiles:
		fileThread = threading.Thread(target=remakeThreads, args=(file, tracker, dictionaryForOldFiles[file][1], dictionaryForOldFiles[file][0]))
		fileThread.start()
		tracker += 1

def remakeThreads(fileName, fileNum, link, bytesRecord):
	
	completionTracker[fileNum] = 0
	recordsList.append(dict())
	
	for i in bytesRecord:
		downloadedByteRange = bytesRecord[i]
		totalFileSize = getFileSize(link)
		sizeForEachThread = totalFileSize/len(bytesRecord)
		byteRange = (bytesRecord[i][1]+1, int(sizeForEachThread*(int(i)+1))-1)
		resumeDownloadThread = threading.Thread(target=resumeDownload, args=(fileName, link, byteRange,fileNum, i, len(bytesRecord)))
		resumeDownloadThread.start()


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

		recordsList[fileNum][threadNum] = (byteRange[0], countBytes+increment)
		

		with open(saveOnAddress+fileName+" Record.json", "w") as record:
			record.write(json.dumps(recordsList[fileNum]))

		countBytes += 51200

		if(countBytes+51199) > byteRange[1]: increment = byteRange[1]-countBytes

	completionTracker[fileNum] += 1

	if(completionTracker[fileNum] == numberOfOldThreads): downloadComplete(fileName, numberOfOldThreads) 



