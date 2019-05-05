import os
import urllib.request
import Metrics
import time

def getFileSize(url):
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers={'User-Agent':user_agent,}
	req = urllib.request.Request(url, None, headers)
	data = urllib.request.urlopen(req)
	return float(data.info()['Content-Length'])


def acceptsByteRange(url):
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers={'User-Agent':user_agent,}
	req = urllib.request.Request(url, None, headers)
	data = urllib.request.urlopen(req)
	return str(data.getheader('Accept-Ranges')) == "bytes"


def downloadComplete(fileName, numOfThreads, metricNum):

	print(fileName, "is completed!")

	for i in range(numOfThreads):
		with open(str(i) + fileName, "rb") as aFile:
			data = aFile.read()
		with open(fileName, "ab") as output:
			output.write(data)
	deleteParts(fileName, numOfThreads, metricNum)


def deleteParts(fileName, numOfThreads, metricNum):

	Metrics.filesDownloading.pop(metricNum)

	for i in range(numOfThreads):
		os.remove(str(i)+fileName)
	os.remove(fileName + " Record.json")

	checkForTermination()


def checkForTermination():
	if not Metrics.filesDownloading:
		os.system("cls")
		print("All downloads are complete!")
		time.sleep(5)
		os.system("exit")

