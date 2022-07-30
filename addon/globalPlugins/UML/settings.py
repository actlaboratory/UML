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
        langLabel = wx.StaticText(self, wx.ID_ANY, label=lang, name=lang)
        self.langList = wx.ListBox(self, wx.ID_ANY, name=lang)
        self.langList.InsertItems([_("Japanese"), _("non-Japanese")], 0)

        strategy = _("Switching strategy")
        strategyLabel = wx.StaticText(
            self, wx.ID_ANY, label=strategy, name=strategy)
        self.strategyList = wx.ListBox(self, wx.ID_ANY, name=strategy)
        self.strategyList.InsertItems([_("Word"), _("Sentence")], 0)

        ok = wx.Button(self, wx.ID_OK, _("OK"))
        ok.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))

        lsz = wx.BoxSizer(wx.HORIZONTAL)
        lsz.Add(langLabel, 1, wx.EXPAND)
        lsz.Add(self.langList, 1, wx.EXPAND)

        ssz = wx.BoxSizer(wx.HORIZONTAL)
        ssz.Add(strategyLabel, 1, wx.EXPAND)
        ssz.Add(self.strategyList, 1, wx.EXPAND)

        bsz = wx.BoxSizer(wx.HORIZONTAL)
        bsz.Add(ok, 1, wx.EXPAND)
        bsz.Add(cancel, 1, wx.EXPAND)

        msz = wx.BoxSizer(wx.VERTICAL)
        msz.Add(lsz, 1, wx.EXPAND)
        msz.Add(ssz, 1, wx.EXPAND)
        msz.Add(bsz, 1, wx.EXPAND)
        self.SetSizer(msz)

    def GetData(self):
        return None
