#--------------------IMPORTS------------------#

import os
import socket
import Metrics
import time

#--------------------This function takes a url and returns hosting server and directory of the file on server.----------------#

def getHost(url):

	doubleSlashes = url.find("//")
	endSlash = url[doubleSlashes+2 : ].find("/") + doubleSlashes+2
	print(url[doubleSlashes+2 : endSlash])
	return url[doubleSlashes+2 : endSlash], url[ endSlash : ]

#-------------------This funciton takes a url and socket, receives 8k bytes from server----------------------#

def getFileSizeAndCheckByteRange(url, sock):
	
	firstReply = sock.recv(8190) 
	header = firstReply[ : firstReply.find(b'\r\n\r\n')] #Seperate header from the data.
	note = len(header) #Store the length of the header.
	header = str(header).split('\\r\\n') #Each attribute in header is seperated by '\r\n'. 

	acceptsByteRanges = False #Assume that the server doesn't accept byteRange.

	for term in header: #For every attribute in header
		
		if "Accept-Ranges: bytes" in term: #If this attribute is set to bytes than server can accept byte ranges and multiple threads can be used for one file. 
			acceptsByteRanges = True

		elif "Content-Length: " in term: #Size of the file 
			totalSize = int(term[16 : ])

	return acceptsByteRanges, totalSize, firstReply[note+4 : ] #firstReply[note+4:] is the data that came with 8k bytes reply. 


#------------------This function is called by every multiple connection file when all of its thread have reached their byte range.

def downloadComplete(fileName, numOfThreads, metricNum):

	print(fileName, "is completed!")

	#Merge the files from every connection.

	for i in range(numOfThreads): 
		with open(str(i) + fileName, "rb") as aFile:
			data = aFile.read()
		with open(fileName, "ab") as output:
			output.write(data)

	deleteParts(fileName, numOfThreads, metricNum)

#-----------------This function deletes the files that were downloaded by each thread, as they all have been merged.-------------#

def deleteParts(fileName, numOfThreads, metricNum):

	Metrics.filesDownloading.pop(metricNum) #Remove the file from filesDownloading dictionary, so that its metrics aren't shown.

	for i in range(numOfThreads):
		os.remove(str(i)+fileName)
	os.remove(fileName + " Record.json") #Delte the record file for this download.

	checkForTermination()

#---------------This function terminates the program if no file is present in filesDownloading dictionary in Metrics.py file.-------------#

def checkForTermination():
	if not Metrics.filesDownloading:
		os.system("cls")
		print("All downloads are complete!")
		time.sleep(5)
		os.system("exit")

