#------------------------IMPORTS----------------------#

import os
import json
import socket
import threading
import time
import CommonFunctions
import Metrics


#----------------------This function seperates the files that are to be resumed from the files that have to be freshly downloaded.
#----------------------This function is calledfrom client.py file.----------------------------------------------------------------#

def seperateFiles(filesToDownload, urls, addressOnDisk):

	saveOnAddress = addressOnDisk #Global variable containing address for download files is set.

	for file in filesToDownload:

		if (file + " Record.json") in os.listdir(addressOnDisk): #If record file exists for this particular file, then it can be resumed.
			
			with open(file+" Record.json") as fin: #Read the dictionary from the file.
				recordDictionary = json.load(fin)
			
			print("Resuming", file)
			
			recordsDictForOldFiles[file] = (Metrics.fileNumber, recordDictionary, urls[file]) #Every file that is to be resumed has an entry in this dictionary.
			Metrics.fileNumber += 1

		else: #If record file doesn't exist, file is put in the list of files that have to be downloaded from start.
			newFiles.append(urls[file])

	makeThreadsToResumeFiles(recordsDictForOldFiles) #Function used for the files that have to resumed.

	return newFiles #Return the list of new files to the caller in client.py


#-----------------------This function makes threads for files, so that multiple files can be downloaded in parallel-----------------#

def makeThreadsToResumeFiles(dictionaryForOldFiles):
 
	global tracker

	for file in dictionaryForOldFiles:
		fileThread = threading.Thread(target=remakeThreads, args=(file, tracker, dictionaryForOldFiles[file][2], dictionaryForOldFiles[file][1], dictionaryForOldFiles[file][0]))
		fileThread.start()
		tracker += 1

#-----------------------This function remakes a thread for a connection used in downloading a file.

def remakeThreads(fileName, fileNum, link, bytesRecord, metricNum):

	completionTracker[fileNum] = 0 #This dictionary is same as mergeDictionary in MultipleConnectionDownloading.py. It keeps track of how many connections completed their download range.
	recordsList.append(dict()) #Records list does the same thing it was doing in the other file.

	Metrics.filesDownloading[metricNum] = [bytesRecord["-1"], 0, 0.0, 0] #bytesRecord["-1"] has the number of bytes already downloaded.
	bytesRecord.pop("-1")
	
	#Creating socket

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host, directoryOnServer = CommonFunctions.getHost(link)
	s.connect((host, 80))

	query = 'GET ' + directoryOnServer + ' HTTP/1.0\r\nHOST: ' + host +' \r\n\r\n'
	s.sendall(query.encode())

	a, totalFileSize, f  = CommonFunctions.getFileSizeAndCheckByteRange(link, s) #Function returns three values, but we only need the middle one.
	s.close()

	Metrics.filesDownloading[metricNum][3] = totalFileSize
	sizeForEachThread = totalFileSize/len(bytesRecord) #Each thread will download this much data. 

	for i in bytesRecord: #bytesRecord now contains the info about the thread num and their downloaded range when the download was interrupted.
		
		byteRange = (bytesRecord[i][1]+1, int(sizeForEachThread*(int(i)+1))-1) #byteRange now will be different than the previous one.
		
		#Resume the old threads.
		resumeDownloadThread = threading.Thread(target=resumeDownload, args=(fileName, link, byteRange,fileNum, i, len(bytesRecord), metricNum) )
		resumeDownloadThread.start()


#--------------------This function is main function in this file. It downloads a file between specific byte ranges.
#--------------------Every connection/thread of a file will call this function. Almost same as downloadFile function
#--------------------in MultipleConnectionDownloading.py file.-----------------------------------------------------#

def resumeDownload(fileName, link, byteRange, fileNum, threadNum, numberOfOldThreads, metricNum):

	downloaded = byteRange[0] #This variable now contains the number of bytes already downloaded.

	host, directoryOnServer = CommonFunctions.getHost(link)

	#Creating socket.

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, 80))

	bytesToDownload = 'bytes=%s-%s' % (byteRange[0], byteRange[1]) #Header accepts byte range in this format.

	query = 'GET ' + directoryOnServer + ' HTTP/1.0\r\nHOST: ' + host +' \r\nRange: ' + bytesToDownload + ' \r\n\r\n' #This get query will be sent to server.

	chunk = 20480 #This variable specifies the number of bytes that will be downloaded in one go.
	tha = False #This variable is used to differentiate header from the data.

	start = time.time()

	sock.sendall(query.encode())
	
	while downloaded <= byteRange[1]: #Loop until the thread has reached its download limit.

		temp = b'' #Server's reply will be stored in this variable
		
		missed = chunk #This variable is used because server often doesn't send all 'chunk' no. of bytes in one go. Then, this variable is used to get the remaining bytes.
				
		while len(temp) < chunk : #Loop until the amount of data expected in one shot is received.
			temp += sock.recv(missed)
			missed = chunk - len(temp) #missed now contains the number of bytes that were missed by server, and should be received in this shot.
		
		if tha == False and b'\r\n\r\n' in temp: #Header and data are seperated '\r\n\r\n'. This if makes sure that data written on the file doesn't contain header info.
			temp = temp[temp.find(b'\r\n\r\n')+4 : ] #Truncate temp if header is in temp. Content before '\r\n\r\n' is header's.
			tha = True#Set this to true so that this condition won't be checked every time
		
		elif tha == False: #If tha is false, this means that data hasn't been received yet. Whatever the server has sent, must be a part of header.
			temp = b'' #Empty temp because we don't want header to be written on the file

		downloaded += len(temp) #Update downloaded variable so that it contains the correct number of bytes downloaded.

		if downloaded > byteRange[1]: #Server often sends more data then asked. This may cause the thread to download more data than its range. Truncate the extra data in this case.
			temp = temp[ : byteRange[1]-downloaded]
			downloaded -= downloaded-byteRange[1] #Update the variable so that it contains correct number of bytes downloaded.


		#These three lines are used for showing metrics. See Metrics.py for further details

		Metrics.filesDownloading[metricNum][0] += len(temp)
		Metrics.filesDownloading[metricNum][1] += len(temp)
		Metrics.filesDownloading[metricNum][2] = (Metrics.filesDownloading[metricNum][1]/(time.time()-start))/1024

		#These two lines are used to keep track of the bytes downloaded by every thread. The dictionary contains thread number as keys and a tuple representing byte range downloaded
		#by that thread as value.

		recordsList[fileNum][-1] = Metrics.filesDownloading[metricNum][0]+4
		recordsList[fileNum][threadNum] = (byteRange[0], downloaded)

		#The data read from the server has to be written on the file of this thread. After every thread is completed, they'll all be merged.
		with open(saveOnAddress+threadNum+fileName, "ab") as output:
			output.write(temp)

		#Records for the range of bytes downloaded has to be stored on disk, for resuming purpose.
		with open(saveOnAddress+fileName+" Record.json", "w") as record:
			record.write(json.dumps(recordsList[fileNum]))

		#If the number of bytes to be read are less than chunk size, then chunk size needs to be lessened. So that appropriate number of bytes
		#are requested from server in the next shot.
		if downloaded+chunk > byteRange[1]: 
			chunk = byteRange[1]-downloaded

		#Due to some problem that i can't figure out, server often stops sending the data when three or four bytes are left. In that case, we can consider it a complete download.
		if Metrics.filesDownloading[metricNum][0] >= Metrics.filesDownloading[metricNum][3]-4: break


	sock.close()

	completionTracker[fileNum] += 1 #When a thread completes downloading its byte range, an increment is made. This is done to end the download when all threads are done.

	if(completionTracker[fileNum] == numberOfOldThreads): #numOfOldThreads is the number of threads that were previously downloading file. If completionTracker[fileNum] is equal to that, then all threads are done.
		CommonFunctions.downloadComplete(fileName, numberOfOldThreads, metricNum) 


#------------------GLOBAL VARIABLES---------------------#

saveOnAddress = str() #Directory where files will be stored.
recordsList = list() #Downloaded byterange records list that will be written on the disk, for resuming purpose in case of download interrupt.
completionTracker = dict() #A dictionary that monitors the completion of downloading by each thread. it contains file numbers as keys and number of connections that have
						   #downloaded their byte range as value

tracker = 0 #This variable is used as a file number. Incremented for every file.

newFiles = list() #List that will contain those files that have to be downloaded from start.
recordsDictForOldFiles = dict() #This dictionary will keep all the relevant record of those files that will be resumed.

