import urllib.request

def downloadWholeFile(link, filePath):
	f = urllib.request.urlopen(link)
	with open(filePath, "wb") as output:
		output.write(f.read())

		print(filePath[filePath.rfind("/")+1 : ], "file is completed!")
