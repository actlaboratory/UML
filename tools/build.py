# -*- coding: utf-8 -*-
#app build tool
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 guredora <contact@guredora.com>
#Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>
#Copyright (C) 2021 Hiroki Fujii <hfujii@hisystron.com>

#constantsのimport前に必要
from audioop import add
import os
import sys
sys.path.append(os.getcwd())

import datetime
import glob
import hashlib
import json
import math
import shutil
import subprocess
import urllib.request

import buildVars
from tools import bumpup

class build:
	def __init__(self):
		# appVeyorかどうかを判別し、処理をスタート
		appveyor = self.setAppVeyor()
		print("Starting build for %s (appveyor mode=%s)" % (buildVars.ADDON_KEYWORD, appveyor,))

		# パッケージのパスとファイル名を決定
		package_path = "output\\"
		if 'APPVEYOR_REPO_TAG_NAME' in os.environ:
			build_filename = os.environ['APPVEYOR_REPO_TAG_NAME']
			# タグ名とバージョンが違ったらエラー
			if build_filename != buildVars.ADDON_VERSION:
				print("Unexpected tag name. expecting %s." %(buildVars.ADDON_VERSION,))
				exit(-1)
		else:
			build_filename = 'snapshot'
		print("Will be built as %s" % build_filename)

		# addonフォルダの存在を確認
		if not os.path.exists("addon"):
			print("Error: no addon folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")
			exit(-1)

		# 前のビルドをクリーンアップ
		self.clean(package_path)

		# appveyorでのスナップショットの場合はバージョン番号を一時的に書き換え
		# バージョン番号をセット
		if build_filename == "snapshot" and appveyor:
			self.version_number = self.makeSnapshotVersionNumber()
		elif build_filename == "snapshot":
			self.version_number = buildVars.ADDON_VERSION
		else:
			self.version_number = build_filename

		# ビルド
		self.build(package_path, build_filename)
		archive_name = "%s-%s.zip" % (buildVars.ADDON_KEYWORD, build_filename,)
		addon_filename = "%s-%s.nvda-addon" % (buildVars.ADDON_NAME, self.version_number)
		shutil.copyfile(package_path + addon_filename, addon_filename)
		self.makePackageInfo(archive_name, addon_filename, self.version_number, build_filename)
		print("Build finished!")

	def runcmd(self,cmd):
		proc=subprocess.Popen(cmd.split(), shell=True, stdout=1, stderr=2)
		proc.communicate()
		return proc.poll()

	def setAppVeyor(self):
		if len(sys.argv)>=2 and sys.argv[1]=="--appveyor":
			return True
		return False

	def clean(self,package_path):
		if os.path.isdir(package_path):
			print("Clearling previous build...")
			shutil.rmtree("output\\")

	def makeSnapshotVersionNumber(self):
		#日本標準時オブジェクト
		JST = datetime.timezone(datetime.timedelta(hours=+9))
		#Pythonは世界標準時のZに対応していないので文字列処理で乗り切り、それを日本標準時に変換
		dt = datetime.datetime.fromisoformat(os.environ["APPVEYOR_REPO_COMMIT_TIMESTAMP"][0:19]+"+00:00").astimezone(JST)
		major = str(dt.year)[2:4]+str(dt.month).zfill(2)
		minor = str(dt.day)
		patch = str(int(math.floor((dt.hour*3600+dt.minute*60+dt.second)/86400*1000)))
		bumpup.bumpup(major+"."+minor+"."+patch, str(dt.date()))
		return major+"."+minor+"."+patch


	def build(self, package_path, build_filename):
		print("Building...")
		shutil.copyfile("addon\\doc\\en\\readme.md", "public\\readme_en.md")
		shutil.copyfile("addon\\doc\\ja\\readme.md", "public\\readme_ja.md")
		shutil.copytree("public", package_path)
		ret = self.runcmd("scons")
		print("build finished with status %d" % ret)
		if ret != 0:
			sys.exit(ret)


		print("Compressing into package...")
		shutil.make_archive("%s-%s" % (buildVars.ADDON_KEYWORD, build_filename,),'zip',package_path)

	def makePackageInfo(self, archive_name, addon_filename, addon_version, build_filename):
		if "APPVEYOR_REPO_COMMIT_TIMESTAMP" in os.environ:
			#日本標準時オブジェクト
			JST = datetime.timezone(datetime.timedelta(hours=+9))
			#Pythonは世界標準時のZに対応していないので文字列処理で乗り切り、それを日本標準時に変換
			dt = datetime.datetime.fromisoformat(os.environ["APPVEYOR_REPO_COMMIT_TIMESTAMP"][0:19]+"+00:00").astimezone(JST)
			dateStr = "%s-%s-%s" % (str(dt.year), str(dt.month).zfill(2), str(dt.day).zfill(2))
		else:
			dateStr = "this is a local build."
		
		print("computing hash...")
		with open(archive_name, mode = "rb") as f:
			content = f.read()
		package_hash = hashlib.sha1(content).hexdigest()
		with open(addon_filename, mode = "rb") as f:
			content = f.read()
		addon_hash = hashlib.sha1(content).hexdigest()
		print("creating package info...")
		info = {}
		info["package_hash"] = package_hash
		info["patch_filename"] = addon_filename
		info["patch_hash"] = addon_hash
		info["version"] = addon_version
		info["released_date"] = dateStr
		with open("%s-%s_info.json" % (buildVars.ADDON_KEYWORD, build_filename), mode = "w") as f:
			json.dump(info, f)


if __name__ == "__main__":
	build()
