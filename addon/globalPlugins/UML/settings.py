import wx
import addonHandler

try:
    addonHandler.initTranslation()
except BaseException:
    def _(x): return x


class SettingsDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(
            self, None, -1, _("Universal Multilingual settings"), size=(800, 600))
        lang = _("Primary language")
        label = wx.StaticText(self, wx.ID_ANY, label=lang, name=lang)
        self.langList = wx.ListCtrl(self, wx.ID_ANY, name=lang)
        self.langList.InsertItem(0, _("Japanese"))
        self.langList.InsertItem(1, _("Non-Japanese"))
        ok = wx.Button(self, wx.ID_OK, _("OK"))
        ok.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        isz = wx.BoxSizer(wx.VERTICAL)
        isz.Add(label, 1, wx.EXPAND)
        isz.Add(self.langList, 1, wx.EXPAND)
        bsz = wx.BoxSizer(wx.HORIZONTAL)
        bsz.Add(ok, 1, wx.EXPAND)
        bsz.Add(cancel, 1, wx.EXPAND)
        msz = wx.BoxSizer(wx.VERTICAL)
        msz.Add(isz, 1, wx.EXPAND)
        msz.Add(bsz, 1, wx.EXPAND)
        self.SetSizer(msz)

    def GetData(self):
        return None
