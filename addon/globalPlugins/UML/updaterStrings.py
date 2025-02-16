try:
    import addonHandler
    addonHandler.initTranslation()
except BaseException:
    def _(x): return x

ERROR = _("Error")
ERROR_UNABLE_TO_CONNECT = _("Unable to connect to update server.\nCheck your internet connection.")
ERROR_UNABLE_TO_CONNECT_SERVERSIDE = _("Unable to connect to update server.")
ERROR_UPDATE_INFO_INVALID = _("The update information is invalid.\nPlease contact ACT Laboratory for further information.")
ERROR_REQUEST_PARAMETERS_INVALID = _("The request parameter is invalid. Please contact the developer.")
ERROR_DOWNLOADING = _("Error downloading add-on update.")
ERROR_OPENING = _("Failed to open add-on package file at %s - missing file or invalid file format")
ERROR_FAILED_TO_UPDATE = _("Failed to update add-on  from %s.")
NO_UPDATES = _("No updates found.\nYou are using the latest version.")
UPDATER_NOT_REGISTERED = _("The updater is not registered. Please contact the developer.")
UPDATE_NOT_POSSIBLE = _("An update was found, but updating from the current version is not possible. Please visit the software's website. ")
UPDATE_CHECK_TITLE = _("Update check")
UPDATE_CONFIRMATION_TITLE = _("Update confirmation")
UPDATE_CONFIRMATION_MESSAGE = _("{summary} Ver.{newVersion} is available.\nWould you like to update?\nCurrent version: {currentVersion}\nNew version: {newVersion}")
DOWNLOADING = _("Downloading add-on update")
CONNECTING = _("Connecting")
UPDATING = _("Updating add-on")
UPDATING_PLEASE_WAIT = _("Please wait while the add-on is being updated.")
