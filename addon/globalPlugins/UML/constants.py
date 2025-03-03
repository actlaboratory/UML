# Reuse of this source code is prohibited.

import addonHandler
import config
import languageHandler
import os

lang = languageHandler.getLanguage().split("_")[0]
addonDir = os.path.abspath(os.path.dirname(__file__))
addonRootDir = os.path.abspath(os.path.join(addonDir, "..", ".."))

curAddon = addonHandler.Addon(addonRootDir)
addonName = curAddon.manifest["name"]
addonKeyword = curAddon.manifest["keyword"]
addonSummary = curAddon.manifest["summary"]
addonVersion = curAddon.manifest["version"]
addonDocFileName = curAddon.manifest["docFileName"]
homepageURL = "https://actlab.org"
updateURL = "%s/api/checkUpdate" % homepageURL

UPDATER_NEED_UPDATE = 200
UPDATER_LATEST = 204
UPDATER_VISIT_SITE = 205
UPDATER_BAD_PARAM = 400
UPDATER_NOT_FOUND = 404

updaterUserAgent = "HISS-updater"

if os.path.isfile(os.path.join(addonRootDir, "doc", lang, addonDocFileName)):
    docFilePath = os.path.join(addonRootDir, "doc", lang, addonDocFileName)
elif os.path.isfile(os.path.join(addonRootDir, "doc", "en", addonDocFileName)):
    docFilePath = os.path.join(addonRootDir, "doc", "en", addonDocFileName)
else:
    docFilePath = None
