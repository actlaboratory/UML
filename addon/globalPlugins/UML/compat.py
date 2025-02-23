import wx
import gui
import versionInfo

def isCompatibleWith2025():
    return versionInfo.version_year >= 2025

def messageBox(message, title):
    if isCompatibleWith2025():
        gui.message.MessageDialog.alert(message, title)
    else:
        gui.messageBox(message, title, style=wx.CENTER)


def yesno(message, title):
    if isCompatibleWith2025():
        dlg = gui.message.MessageDialog(None, message, title, buttons=gui.message.DefaultButtonSet.YES_NO)
        return dlg.ShowModal() == gui.message.ReturnCode.YES
    else:
        return gui.messageBox(message, title, style=wx.CENTER | wx.YES | wx.NO | wx.ICON_INFORMATION) == wx.YES

