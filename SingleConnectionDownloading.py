import urllib.request
import time
import CommonFunctions
import Metrics


def downloadWholeFile(link, filePath, metricNum):

	print("Single connection downloading!!!")

	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers={'User-Agent':user_agent,}

	start = time.time()

	req = urllib.request.Request(link, None, headers)

	f = urllib.request.urlopen(req)

	while True:

		data = f.read(51200)

		if not data:
			Metrics.filesDownloading.pop(metricNum)
			break

		with open(filePath, "ab") as output:
			output.write(data)

		Metrics.filesDownloading[metricNum][0] += len(data)
		Metrics.filesDownloading[metricNum][1] += len(data)
		Metrics.filesDownloading[metricNum][2] = (Metrics.filesDownloading[metricNum][1]/(time.time()-start))/1024

	print(filePath[filePath.rfind("/")+1 : ], "file is completed!")
