#------------------IMPORTS---------------------#

import sys
import threading
import ResumeDownload
import MultipleConnectionDownloading
import Metrics

#---------------------This function parses the command line arguments and extracts the tags---------------#

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


#----------------This function creates new download threads for every file that has to be downloaded from start.-----------------#

def startNewFiles(newFiles):
	
	global no
	for file in newFiles:
		fileName = file[file.rfind("/")+1 : ]
		threading.Thread(target=MultipleConnectionDownloading.processThreadsForFiles, args=(file, fileName, no, simulConn, sA)).start()
		no += 1

#------------------MAIN PROGRAM-------------------#

resumeDownload, simulConn, interval, fTD, sA, fA = parseArguments()

no = 0 #This function is used as an id by every new file. Incremeneted for every file.
files = list() #This list will contain the names of all the files
filesAndUrls = dict() #This dictionary will contain fileName as keys and their urls as values.

for file in fA:
	
	fileName = file[file.rfind("/")+1 : ]
	files.append(fileName)
	filesAndUrls[fileName] = file
	
if resumeDownload:
	newFiles = ResumeDownload.seperateFiles(files,filesAndUrls, sA)
else: 
	newFiles = fA #If resumeDownload is false, all the files have to be downloaded from start.

startNewFiles(newFiles)

threading.Thread(target=Metrics.startSchedule, args=(interval,)).start() #Start scheduler.