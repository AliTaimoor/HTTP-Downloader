import os
import json
import urllib.request
import threading
import time
from CommonFunctions import *
import Metrics

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
			recordsDictForOldFiles[file] = (Metrics.fileNumber, recordDictionary, urls[file])
			Metrics.fileNumber += 1

		else:
			newFiles.append(urls[file])

	makeThreadsToResumeFiles(recordsDictForOldFiles)

	return newFiles


def makeThreadsToResumeFiles(dictionaryForOldFiles):
 
	global tracker

	for file in dictionaryForOldFiles:
		fileThread = threading.Thread(target=remakeThreads, args=(file, tracker, dictionaryForOldFiles[file][2], dictionaryForOldFiles[file][1], dictionaryForOldFiles[file][0]))
		fileThread.start()
		tracker += 1

def remakeThreads(fileName, fileNum, link, bytesRecord, metricNum):
	
	completionTracker[fileNum] = 0
	recordsList.append(dict())

	Metrics.filesDownloading[metricNum] = [bytesRecord["-1"], 0, 0.0, 0]
	bytesRecord.pop("-1")
	
	for i in bytesRecord:
		downloadedByteRange = bytesRecord[i]
		totalFileSize = getFileSize(link)
		Metrics.filesDownloading[metricNum][3] = totalFileSize
		sizeForEachThread = totalFileSize/len(bytesRecord)
		byteRange = (bytesRecord[i][1]+1, int(sizeForEachThread*(int(i)+1))-1)
		resumeDownloadThread = threading.Thread(target=resumeDownload, args=(fileName, link, byteRange,fileNum, i, len(bytesRecord), metricNum) )
		resumeDownloadThread.start()


def resumeDownload(fileName, link, byteRange, fileNum, threadNum, numberOfOldThreads, metricNum):

	countBytes = byteRange[0]
	increment = 51199

	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers={'User-Agent':user_agent,}

	start = time.time()

	while countBytes <= byteRange[1]:

		req = urllib.request.Request(link, None, headers)
		bytesToDownload = 'bytes=%s-%s' % (countBytes, countBytes+increment)
		req.add_header("Range", bytesToDownload)
		f = urllib.request.urlopen(req)

		with open(saveOnAddress+threadNum+fileName, "ab") as output:
			output.write(f.read())

		Metrics.filesDownloading[metricNum][0] += increment
		Metrics.filesDownloading[metricNum][1] += increment
		Metrics.filesDownloading[metricNum][2] = (Metrics.filesDownloading[metricNum][1]/(time.time()-start))/1024

		recordsList[fileNum][-1] = Metrics.filesDownloading[metricNum][0]
		recordsList[fileNum][threadNum] = (byteRange[0], countBytes+increment)
	
		with open(saveOnAddress+fileName+" Record.json", "w") as record:
			record.write(json.dumps(recordsList[fileNum]))

		countBytes += 51200

		if(countBytes+51199) > byteRange[1]: increment = byteRange[1]-countBytes

	completionTracker[fileNum] += 1

	if(completionTracker[fileNum] == numberOfOldThreads): downloadComplete(fileName, numberOfOldThreads, metricNum) 



