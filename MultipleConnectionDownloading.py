import threading
import urllib.request
import json
from CommonFunctions import * 
from SingleConnectionDownloading import *
import Metrics
import time


def downloadfile(link, byteRange, fileName, fileNum, threadNum, mN):

	byteRange = (int(byteRange[0]), int(byteRange[1]))

	countBytes = byteRange[0]
	increment = 51199

	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers={'User-Agent':user_agent,}

	start = time.time()

	while countBytes <= byteRange[1]:

		req = urllib.request.Request(link, None, headers)
		bytesToDownload = 'bytes=%s-%s' % (countBytes, countBytes+increment)
		req.add_header('Range', bytesToDownload)
		f = urllib.request.urlopen(req)


		with open(storeAddress+fileName, 'ab') as output:
			output.write(f.read())

		Metrics.filesDownloading[mN][0] += increment
		Metrics.filesDownloading[mN][1] += increment
		Metrics.filesDownloading[mN][2] = (Metrics.filesDownloading[mN][1]/(time.time()-start))/1024

		listOfRecords[fileNum][-1] = Metrics.filesDownloading[mN][0]
		listOfRecords[fileNum][threadNum] = (byteRange[0], countBytes+increment)

		with open(storeAddress+fileName[1:]+" Record.json", "w") as record:
			record.write(json.dumps(listOfRecords[fileNum]))

		countBytes += 51200

		if (countBytes+51199) > byteRange[1]: increment = byteRange[1]-countBytes

	mergeDictionary[fileNum] += 1
	if mergeDictionary[fileNum] == numOfSimulConn: 
		downloadComplete(fileName[1:], numOfSimulConn, mN)
	
		
def createNewDownloadThread(link, byteRange, fileName, fileNum, threadNum, mN):
	download_thread = threading.Thread(target=downloadfile, args=(link, byteRange, fileName, fileNum, threadNum, mN))
	download_thread.start()


def startMakingConnections(numOfThreads, fileName, fileAddress, sizeForEachThread, fileNum, mN):
	
	for i in range(numOfThreads):
		#print(i)
		createNewDownloadThread(fileAddress, (i*sizeForEachThread, ((i+1)*sizeForEachThread-1)), str(i)+fileName, fileNum, i, mN)


def processThreadsForFiles(file, fileName, fileNum, simulConn, sA):
	

	global numOfSimulConn
	global storeAddress
	global number
	
	numOfSimulConn = simulConn
	storeAddress = sA
	
	
	if acceptsByteRange(file):
		listOfRecords.append({-1 : 0})
		fileSize = getFileSize(file)
		#print("File Size:", fileSize)
		sizeForEachThread = fileSize/numOfSimulConn
		#print("Size for each thread:", sizeForEachThread)
		Metrics.filesDownloading[Metrics.fileNumber] = [0, 0, 0.0, fileSize]
		Metrics.fileNumber += 1
		mergeDictionary[number] = 0
		print("Metric number:", Metrics.fileNumber)
		startMakingConnections(numOfSimulConn, fileName, file, sizeForEachThread, number, Metrics.fileNumber-1)
		number += 1

	else:
		try:
			metricList = [0, 0, 0.0, CommonFunctions.getFileSize(file)]
			Metrics.filesDownloading[Metrics.fileNumber] = metricList
			Metrics.fileNumber += 1
			threading.Thread(target=downloadWholeFile, args=(file, storeAddress+fileName, Metrics.fileNumber-1)).start()
		except:
			print("The link", file, "doesn't contain any downloadable content!")

listOfRecords = list()
mergeDictionary = dict()
numOfSimulConn, number, storeAddress = 0, 0, ""