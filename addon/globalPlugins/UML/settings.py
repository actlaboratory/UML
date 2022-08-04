import wx
import addonHandler
import copy
import synthDriverHandler
from . import engineSelection

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

        # Need to exclude Universal Multilingual itself and silence.
        # [0]: internal identifier, [1]: display name
        self.synths = [x for x in synthDriverHandler.getSynthList() if x[0] not in [
            "UML", "silence"]]
        self.engineMap = copy.copy(opts["engineMap"])

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
        enginesLabel = wx.StaticText(
            self, wx.ID_ANY, label=engines, name=engines)
        self.enginesList = wx.ListCtrl(
            self, wx.ID_ANY, name=engines, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.enginesList.AppendColumn(_("Language"), wx.LIST_FORMAT_LEFT)
        self.enginesList.AppendColumn(_("Engine"), wx.LIST_FORMAT_LEFT)
        self._updateEngineList(self.enginesList, self.engineMap, self.synths)
        sbtnLabel = _("Select engine")
        self.selectEngineButton = wx.Button(
            self, wx.ID_ANY, label=sbtnLabel, name=sbtnLabel)
        self.selectEngineButton.Bind(wx.EVT_BUTTON, self.onSynthSelect)

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

    def _updateEngineList(self, ctrl, engineMap, synths):
        ctrl.DeleteAllItems()
        for elem in self.langValues:
            resolved = self._findSynthDisplayName(
                self.synths, engineMap[elem["internal"]])
            stat = resolved if resolved != "" else _("Not set")
            ctrl.Append((elem["user"], stat))

    def _findSynthDisplayName(self, synths, target):
        for elem in synths:
            if elem[0] == target:
                return elem[1]
            # end found
        # end for
        return ""

    def GetData(self):
        return {
            "primary_language": self.langValues[self.langList.GetSelection()]["internal"],
            "strategy": self.strategyValues[self.strategyList.GetSelection()]["internal"],
            "engineMap": self.engineMap,
        }

    def onSynthSelect(self, evt):
        selected = self.enginesList.GetFocusedItem()
        if selected == -1:
            return
        lang = self.langValues[selected]["user"]
        focus = self.engineMap[self.langValues[selected]["internal"]]
        dlg = engineSelection.EngineSelectionDialog(self.synths, lang, focus)
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            self.engineMap[self.langValues[selected]
                           ["internal"]] = dlg.GetData()
            self._updateEngineList(
                self.enginesList, self.engineMap, self.synths)
        dlg.Destroy()
