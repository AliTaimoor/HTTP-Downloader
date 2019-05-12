#--------------------------------IMPORTS-----------------------------------#

import sched, time
import os


#------------------This function schedules the showMetrics function to run every 'interval' secs.

def startSchedule(interval):

	s.enter(interval, 1, showMetrics, (s, interval)) #(s, interval) are the arguments that will be passed to showMetrics function.
	s.run()

#------------------This function will be called every 'interval' seconds to display the metrics of on-going downloads. #sc is a scheduler object.

def showMetrics(sc, interval):

	os.system("cls") #Clear the previous metrics from screen.

	for file in filesDownloading: #filesDownloading contains the metric number of all those files that are being downloaded.

		if filesDownloading[file][3] == 0: continue #If total size of a file is not present in this list, then we can't show metrics. Wait for the next scheduled  call.

		done = (filesDownloading[file][0]/filesDownloading[file][3])*100 #done percent file downloaded.
		print("File Number:", file, "\t", filesDownloading[file][0], "/", filesDownloading[file][3], "Download speed:", filesDownloading[file][2])
		print(done, "%")
		print("#" * int(done))

	s.enter(interval, 1, showMetrics, (sc, interval)) #Reschedule the function again for 'interval' seconds.

	print("\n\n")


#---------------------GLOBAL VARIABLES--------------------#


#This variable is used by every file that has to be downloaded. It is used in other files as metric number i.e. number used to identify 
#metrics of a particular file in filesDownloading dictionary.
fileNumber = 0

#This dictionary contains metric number of all those files that are being downloaded. Metric number is key of dictionary and the value is
#a list that has four elements. [a,b,c,d] where a is total number of bytes downloaded, b is total number of bytes downloaded in this session,
#c is the download speed in kbps, and d is the size of file.
filesDownloading = dict()

#Scheduler object
s = sched.scheduler(time.time, time.sleep)
