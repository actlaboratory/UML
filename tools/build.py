# -*- coding: utf-8 -*-
#app build tool
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2024 guredora <contact@guredora.com>
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
		# Github actionsなどの自動実行かどうかを判別し、処理をスタート
		automated = self.setAutomated()
		print("Starting build for %s(automated mode=%s)" % (buildVars.ADDON_KEYWORD, automated,))

		# パッケージのパスとファイル名を決定
		package_path = "output\\"
		build_filename = os.environ.get('TAG_NAME', 'snapshot')
		# snapshotではなかった場合は、タグ名とバージョンが違ったらエラー
		if (build_filename != "snapshot") and (build_filename != buildVars.ADDON_VERSION):
			print("Unexpected tag name. expecting %s." %(buildVars.ADDON_VERSION,))
			exit(-1)
		print("Will be built as %s" % build_filename)

		# addonフォルダの存在を確認
		if not os.path.exists("addon"):
			print("Error: no addon folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")
			exit(-1)

		# 前のビルドをクリーンアップ
		self.clean(package_path)

		# 自動実行でのスナップショットの場合はバージョン番号を一時的に書き換え
		if build_filename == "snapshot" and automated:
			print(self.makeSnapshotVersionNumber())

		# ビルド
		self.build(package_path, build_filename)
		archive_name = "%s-%s.zip" % (buildVars.ADDON_KEYWORD, build_filename,)
		addon_filename = "%s-%s.nvda-addon" % (buildVars.ADDON_NAME, buildVars.ADDON_VERSION,)
		shutil.copyfile(package_path + addon_filename, addon_filename)
		self.makePackageInfo(archive_name, addon_filename, build_filename)
		print("Build finished!")

	def runcmd(self,cmd):
		proc=subprocess.Popen(cmd.split(), shell=True, stdout=1, stderr=2)
		proc.communicate()
		return proc.poll()

	def setAutomated(self):
		return os.environ.get("GITHUB_ACTIONS", "false") == "true"

	def clean(self,package_path):
		if os.path.isdir(package_path):
			print("Clearling previous build...")
			shutil.rmtree("output\\")

	def makeSnapshotVersionNumber(self):
		#日本標準時オブジェクト
		JST = datetime.timezone(datetime.timedelta(hours=+9))
		dt = datetime.datetime.fromisoformat(os.environ["COMMIT_TIMESTAMP"]).astimezone(JST)
		major = f"{dt.year % 100:02d}{dt.month:02d}"
		minor = str(dt.day)
		patch = str(int(math.floor((dt.hour*3600+dt.minute*60+dt.second)/86400*1000)))
		buildVars.ADDON_VERSION = major+"."+minor+"."+patch
		buildVars.ADDON_RELEASE_DATE = str(dt.date())
		bumpup.bumpup(major+"."+minor+"."+patch, str(dt.date()))
		return major+"."+minor+"."+patch

	def build(self, package_path, build_filename):
		print("Building...")
		os.mkdir(package_path)
		shutil.copyfile("addon\\doc\\en\\readme.md", os.path.join(package_path, "readme_en.txt"))
		shutil.copyfile("addon\\doc\\ja\\readme.md", os.path.join(package_path, "readme_ja.txt"))
		shutil.copyfile("license", os.path.join(package_path, "license.txt"))
		ret = self.runcmd("scons")
		print("build finished with status %d" % ret)
		if ret != 0:
			sys.exit(ret)
		print("Compressing into package...")
		shutil.make_archive("%s-%s" % (buildVars.ADDON_KEYWORD, build_filename,),'zip',package_path)

	def makePackageInfo(self, archive_name, addon_filename, build_filename):
		print("Calculating  hash...")
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
		info["version"] = buildVars.ADDON_VERSION
		info["released_date"] = buildVars.ADDON_RELEASE_DATE
		with open("%s-%s_info.json" % (buildVars.ADDON_KEYWORD, build_filename,), mode = "w") as f:
			json.dump(info, f)


if __name__ == "__main__":
	build()
