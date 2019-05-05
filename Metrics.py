import sched, time
import os
import sys

fileNumber = 0
filesDownloading = dict()

s = sched.scheduler(time.time, time.sleep)

def startSchedule(interval):

	s.enter(interval, 1, showMetrics, (s, interval))
	s.run()

def showMetrics(sc, interval):

	os.system("cls")

	for file in filesDownloading:

		if filesDownloading[file][3] == 0: continue

		#if filesDownloading[file][0] == -1:
		#	filesDownloading[file][1] = sys.getsizeof(filesDownloading[file][4])
		#	filesDownloading[file][2] = (filesDownloading[file][1]/(time.time()-filesDownloading[file][5]))/1024
		#	done = (filesDownloading[file][1]/filesDownloading[file][3])*100
		#	 
		#	print("File Number:", file, "\t", filesDownloading[file][1], "/", filesDownloading[file][3], "Download speed:", filesDownloading[file][2])
		#	print(done, "%")
		#	print("#" * int(done))
		#	continue
		
		done = (filesDownloading[file][0]/filesDownloading[file][3])*100
		print("File Number:", file, "\t", filesDownloading[file][0], "/", filesDownloading[file][3], "Download speed:", filesDownloading[file][2])
		print(done, "%")
		print("#" * int(done))

	s.enter(interval, 1, showMetrics, (sc, interval))

	print("\n\n")