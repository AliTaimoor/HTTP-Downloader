import socket
import time
import CommonFunctions
import Metrics


def downloadWholeFile(link, filePath, sock, data, totalSize, metricNum):

	print("Single connection downloading!!!")
	print("Total SIze:", totalSize)

	host, directoryOnServer = CommonFunctions.getHost(link)

	start = time.time()

	with open("t.mp4", "wb") as file:
		file.write(data)

	downloaded, chunkSize = len(data), 20480

	while downloaded <= totalSize:
		missed = 20480
		data = b''
		while len(data) < chunkSize:
			data += sock.recv(missed)
			missed = 20480-len(data)
		downloaded += chunkSize
		if downloaded+chunkSize > totalSize: chunkSize = totalSize-downloaded

		with open("t.mp4", "ab") as file:
			file.write(data)

		Metrics.filesDownloading[metricNum][0] += len(data)
		Metrics.filesDownloading[metricNum][1] += len(data)
		Metrics.filesDownloading[metricNum][2] = (Metrics.filesDownloading[metricNum][1]/(time.time()-start))/1024

	Metrics.filesDownloading.pop(metricNum)

	print(filePath[filePath.rfind("/")+1 : ], "file is completed!")

	
