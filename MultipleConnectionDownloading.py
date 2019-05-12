#------------------IMPORTS-------------------#


import threading
import socket
import json
from CommonFunctions import * 
from SingleConnectionDownloading import *
import Metrics
import time


#---------------This function is the main function in this file. it downloads file between specific byte ranges.
#---------------Every thread of a file will call this function.-------------------------------------------------#

def downloadfile(host, directoryOnServer, initialData, link, byteRange, fileName, fileNum, threadNum, mN):

	byteRange = (int(byteRange[0]), int(byteRange[1])) #Tuple defines the range of bytes that will be downloaded
	
	#Creating socket

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, 80))

	downloaded = byteRange[0] #This variable keeps track of the number of bytes downloaded by a particular thread.

	start = time.time() #Start time for downloading, used to calculate download speed.

	bytesToDownload = 'bytes=%s-%s' % (byteRange[0], byteRange[1]) #Socket get request header takes an argument in this format for byte range.
		
	query = 'GET ' + directoryOnServer + ' HTTP/1.0\r\nHOST: ' + host +' \r\nRange: ' + bytesToDownload + ' \r\n\r\n' #This get query will be sent to the server.

	sock.sendall(query.encode())

	chunk = 10240 #This variable specifies the number of bytes that will be downloaded in one go.
	tha = False #This variable is used to differentiate header from data when server replies.
		
	while  downloaded < byteRange[1]: #Loop until the thread has reached its download range
		
		temp = b'' #Server's reply will be stored in this variable
		
		missed = chunk #This variable is used because server often doesn't send all 'chunk' no. of bytes in one go. Then, this variable is used to get the remaining bytes.
		
		while len(temp) < chunk : #Loop until the amount of data expected in one shot is received.
			temp += sock.recv(missed)
			missed = chunk - len(temp) #missed now contains the number of bytes that were missed by server, and should be received in this shot.
		
		if tha == False and b'\r\n\r\n' in temp: #Header and data are seperated '\r\n\r\n'. This if makes sure that data written on the file doesn't contain header info.
			temp = temp[temp.find(b'\r\n\r\n')+4 : ] #Truncate temp if header is in temp. Content before '\r\n\r\n' is header's.
			tha = True #Set this to true so that this condition won't be checked every time.
		
		elif tha == False: #If tha is false, this means that data hasn't been received yet. Whatever the server has sent, must be a part of header.
			temp = b'' #Empty temp because we don't want header to be written on the file

		downloaded += len(temp) #Update downloaded variable so that it contains the number of bytes downloaded by this thread.

		if downloaded > byteRange[1]: #Server often sends more data then asked. This may cause the thread to download more data than its range. Truncate the extra data in this case.
			temp = temp[ : byteRange[1]-downloaded]
			downloaded -= downloaded-byteRange[1] #Update the variable so that it contains correct number of bytes downloaded.


		#These three lines are used for showing metrics. See Metrics.py for further details

		Metrics.filesDownloading[mN][0] += len(temp) 
		Metrics.filesDownloading[mN][1] += len(temp)
		Metrics.filesDownloading[mN][2] = (Metrics.filesDownloading[mN][1]/(time.time()-start))/1024

		#These two lines are used to keep track of the bytes downloaded by every thread. The dictionary contains thread number as keys and a tuple representing byte range downloaded
		#by that thread as value.		

		listOfRecords[fileNum][-1] = Metrics.filesDownloading[mN][0]+4
		listOfRecords[fileNum][threadNum] = (byteRange[0], downloaded)

		#Records for the range of bytes downloaded has to be stored on disk, for resuming purpose.
		with open(storeAddress+fileName[1:]+" Record.json", "w") as record:
			record.write(json.dumps(listOfRecords[fileNum]))

		#The data read from the server has to be written on the file of this thread. After every thread is completed, they'll all be merged.
		with open(storeAddress+fileName, 'ab') as output:
			output.write(temp)
		
		#If the number of bytes to be read are less than chunk size, then chunk size needs to be lessened. So that appropriate number of bytes
		#are requested from server in the next shot.
		if downloaded + chunk > byteRange[1] :
			chunk = byteRange[1]-downloaded

	
	sock.close()
	
	mergeDictionary[fileNum] += 1 #When a thread completes downloading its byte range, an increment is made. This is done to end the download when all threads are done.
	
	if mergeDictionary[fileNum] == numOfSimulConn: #numOfSimulConn is the number of threads. if mergeDictioanary[fileNum] is equal to that, then all threads are done.
		CommonFunctions.downloadComplete(fileName[1:], numOfSimulConn, mN)
	

#--------------------------This function creates a thread for a connection of a file, and then that thread calls the downloadFile function.--------------------------#
		
def createNewDownloadThread(host, directoryOnServer, initialData, link, byteRange, fileName, fileNum, threadNum, mN):
	download_thread = threading.Thread(target=downloadfile, args=(host, directoryOnServer, initialData, link, byteRange, fileName, fileNum, threadNum, mN))
	download_thread.start()


#--------------------------This function defines the range of bytes to be downloaded by a thread, that is to be made in the createNewDownloadThread.------------------# 

def startMakingConnections(host, directoryOnServer, initialData, numOfThreads, fileName, fileAddress, sizeForEachThread, fileNum, mN):
	
	for i in range(numOfThreads):
		
		startByte = (i*sizeForEachThread)
		endByte = ((i+1)*sizeForEachThread)-1
		
		createNewDownloadThread(host, directoryOnServer, initialData, fileAddress, (startByte, endByte), str(i)+fileName, fileNum, i, mN)


#--------------------------This function is called for every file that will be downloaded. This function is called fromm client.py-------------------------------------#

def processThreadsForFiles(file, fileName, fileNum, simulConn, sA):
	

	global numOfSimulConn #Number of simultaneous connnections i.e. Number of threads for each file.
	global storeAddress #Directory where the downloaded files will be stored.
	global number #This number is assigned to every file that will be downloaded using above written functions. Incremented for each file.
	
	#Assigning argument variables to global variables.

	numOfSimulConn = simulConn 
	storeAddress = sA
	
	#Set up a socket to get the necessary info about the server and file.
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	host, directoryOnServer = CommonFunctions.getHost(file)

	s.connect((host, 80))

	query = 'GET ' + directoryOnServer + ' HTTP/1.0\r\nHOST: ' + host +' \r\n\r\n'
	s.sendall(query.encode())

	acceptsByteRange, totalSize, initialData = CommonFunctions.getFileSizeAndCheckByteRange(file, s) 

	if acceptsByteRange: #File will be downloaded using threading for every connection, using functions within this file.
		s.close()
		listOfRecords.append({-1 : 0}) #This dictionary keeps record of byte ranges downloaded by each thread. Threads are numbered 0 to n. At key -1, the total number of bytes downloaded is stored.
		sizeForEachThread = totalSize/numOfSimulConn #Every thread will download this number of bytes.
		Metrics.filesDownloading[Metrics.fileNumber] = [0, 0, 0.0, totalSize]
		Metrics.fileNumber += 1
		mergeDictionary[number] = 0
		startMakingConnections(host, directoryOnServer, initialData, numOfSimulConn, fileName, file, sizeForEachThread, number, Metrics.fileNumber-1)
		number += 1 #Increment number for the next file.

	else:
		
		try:
			metricList = [len(initialData), len(initialData), 0.0, totalSize]
			Metrics.filesDownloading[Metrics.fileNumber] = metricList
			Metrics.fileNumber += 1

			#This thread is for a file that can't be downloaded by byte range, and hence can't be resumed if interrupted.
			threading.Thread(target=downloadWholeFile, args=(file, storeAddress+fileName, s, initialData, totalSize, Metrics.fileNumber-1)).start()
		
		except:
			print("The link", file, "doesn't contain any downloadable content!")

#listOfRecords is a list that contains contains a dictionary at every index. Each index denotes a file number that is used only in this py file.
#'number' variable is used for this purpose.
listOfRecords = list()

#mergeDictionary contains fileNumber as keys and the number of connections that have completed their downloading as values.
mergeDictionary = dict()

#These variables will later be set to their actual values.
numOfSimulConn, number, storeAddress = 0, 0, ""