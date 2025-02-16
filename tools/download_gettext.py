import urllib.request
import glob
import os
import shutil
import zipfile

def downloadGettext():
	remoteFile = "gettext0.21-iconv1.16-static-64.zip"
	url = "https://github.com/mlocati/gettext-iconv-windows/releases/download/v0.21-v1.16/%s" % remoteFile
	print("Downloading gettext tools from %s" % url)
	urllib.request.urlretrieve(url, "gettext.zip")
	print("Extracting gettext...")
	with zipfile.ZipFile("gettext.zip", "r") as zip:
		lst = zip.namelist()
		for item in lst:
			if item.startswith("bin/"):
				print("extracting %s" % item)
				zip.extract(item)
			# end extract
		# end for
	# end with
	print("moving tools to current directory...")
	for item in glob.glob("bin/*"):
		print("moving %s" % item)
		shutil.move(item, ".")
	# end for
	print("removing temporary files...")
	shutil.rmtree("bin")
	os.remove("gettext.zip")
	print("got gettext tools!")

downloadGettext()
