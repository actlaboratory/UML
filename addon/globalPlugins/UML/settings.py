import wx
import addonHandler

try:
    addonHandler.initTranslation()
except BaseException:
    def _(x): return x


class SettingsDialog(wx.Dialog):
    langValues = [
        {"internal": "ja", "user": _("Japanese")},
        {"internal": "en", "user": _("Non-Japanese")},
    ]
    strategyValues = [
        {"internal": "sentence", "user": _("Sentence")},
        {"internal": "word", "user": _("Word")},
    ]

    def __init__(self, opts):
        wx.Dialog.__init__(
            self, None, -1, _("Universal Multilingual settings"), size=(800, 600))

        lang = _("Primary language")
        langLabel = wx.StaticText(self, wx.ID_ANY, label=lang, name=lang)
        self.langList = wx.ListBox(self, wx.ID_ANY, name=lang)
        self.langList.InsertItems([x["user"] for x in self.langValues], 0)

        strategy = _("Switching strategy")
        strategyLabel = wx.StaticText(
            self, wx.ID_ANY, label=strategy, name=strategy)
        self.strategyList = wx.ListBox(self, wx.ID_ANY, name=strategy)
        self.strategyList.InsertItems([x["user"]
                                       for x in self.strategyValues], 0)

        engines = _("Speech engines")
        enginesLabel = wx.StaticText(self, wx.ID_ANY, label=engines, name=engines)
        self.enginesList = wx.ListCtrl(self, wx.ID_ANY, name=engines, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.enginesList.AppendColumn(_("Language"), wx.LIST_FORMAT_LEFT)
        self.enginesList.AppendColumn(_("Engine"), wx.LIST_FORMAT_LEFT)
        for elem in self.langValues:
            self.enginesList.Append((elem["user"], "not set"))

        ok = wx.Button(self, wx.ID_OK, _("OK"))
        ok.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))

        lsz = wx.BoxSizer(wx.HORIZONTAL)
        lsz.Add(langLabel, 1, wx.EXPAND)
        lsz.Add(self.langList, 1, wx.EXPAND)

        ssz = wx.BoxSizer(wx.HORIZONTAL)
        ssz.Add(strategyLabel, 1, wx.EXPAND)
        ssz.Add(self.strategyList, 1, wx.EXPAND)

        esz = wx.BoxSizer(wx.HORIZONTAL)
        esz.Add(enginesLabel, 1, wx.EXPAND)
        esz.Add(self.enginesList, 1, wx.EXPAND)

        bsz = wx.BoxSizer(wx.HORIZONTAL)
        bsz.Add(ok, 1, wx.EXPAND)
        bsz.Add(cancel, 1, wx.EXPAND)

        msz = wx.BoxSizer(wx.VERTICAL)
        msz.Add(lsz, 1, wx.EXPAND)
        msz.Add(ssz, 1, wx.EXPAND)
        msz.Add(esz, 1, wx.EXPAND)
        msz.Add(bsz, 1, wx.EXPAND)
        self.SetSizer(msz)

        langIndex = self._searchValue(
            self.langValues, lambda x: x["internal"] == opts["primary_language"])
        strategyIndex = self._searchValue(
            self.strategyValues, lambda x: x["internal"] == opts["strategy"])
        self.langList.Select(langIndex)
        self.strategyList.Select(strategyIndex)

    def _searchValue(self, ref, cond):
        i = 0
        for elem in ref:
            if cond(elem):
                return i
            # end found
            i += 1
        # end for
        return 0
    # end _searchValue

    def GetData(self):
        return {
            "primary_language": self.langValues[self.langList.GetSelection()]["internal"],
            "strategy": self.strategyValues[self.strategyList.GetSelection()]["internal"],
        }
