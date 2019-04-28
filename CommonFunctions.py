import os
import urllib.request

def getFileSize(url):
	data = urllib.request.urlopen(url)
	return float(data.info()['Content-Length'])


def acceptsByteRange(url):
	data = urllib.request.urlopen(url)
	return str(data.getheader('Accept-Ranges')) == "bytes"


def downloadComplete(fileName, numOfThreads):

	print(fileName, "is completed!")

	for i in range(numOfThreads):
		with open(str(i) + fileName, "rb") as aFile:
			data = aFile.read()
		with open(fileName, "ab") as output:
			output.write(data)
	deleteParts(fileName, numOfThreads)


def deleteParts(fileName, numOfThreads):
	for i in range(numOfThreads):
		os.remove(str(i)+fileName)
	os.remove(fileName + " Record.json")

