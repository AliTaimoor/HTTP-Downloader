import sys
import json
import os
import threading
import urllib.request
from ResumeDownload import *
from CommonFunctions import *
from SingleConnectionDownloading import *
from MultipleConnectionDownloading import *
import Metrics


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



def startNewFiles(newFiles):
	
	global no
	for file in newFiles:
		fileName = file[file.rfind("/")+1 : ]
		threading.Thread(target=processThreadsForFiles, args=(file, fileName, no, simulConn, sA)).start()
		no += 1

resumeDownload, simulConn, interval, fTD, sA, fA = parseArguments()

no = 0
files = list()
filesAndUrls = dict()

#print(resumeDownload)
#print("Number of simultaneous connection:", simulConn)
#print("Interval", interval)
#print("Number of files to download:", fTD)
#print("Files will be saved on", sA )
#print("Files will be downloaded from:", fA)

#timer = threading.Timer(interval, Metrics.showMetrics, None, None)
#timer.start()

for file in fA:
	
	fileName = file[file.rfind("/")+1 : ]
	files.append(fileName)
	filesAndUrls[fileName] = file
	
if resumeDownload:
	newFiles = seperateFiles(files,filesAndUrls, sA)
else: 
	newFiles = fA

startNewFiles(newFiles)

threading.Thread(target=Metrics.startSchedule, args=(interval,)).start()