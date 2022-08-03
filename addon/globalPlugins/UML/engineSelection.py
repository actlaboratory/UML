import wx
import addonHandler
import synthDriverHandler

try:
    addonHandler.initTranslation()
except BaseException:
    def _(x): return x


class EngineSelectionDialog(wx.Dialog):
    def __init__(self, language, focusedEngineIdentifier=None):
        wx.Dialog.__init__(
            self, None, -1, _("Select synthesizer for %s language") % (language), size=(300, 500))
        # Need to exclude Universal Multilingual itself and silence.
        # [0]: internal identifier, [1]: display name
        synths = [x for x in synthDriverHandler.getSynthList() if x[0] not in ["UML", "silence"]]

        synth = _("Synthesizer")
        synthLabel = wx.StaticText(self, wx.ID_ANY, label=synth, name=synth)
        self.synthList = wx.ListBox(self, wx.ID_ANY, name=synth)
        self.synthList.InsertItems([x[1] for x in synths], 0)
        ok = wx.Button(self, wx.ID_OK, _("OK"))
        ok.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))

        ssz = wx.BoxSizer(wx.HORIZONTAL)
        ssz.Add(synthLabel, 1, wx.EXPAND)
        ssz.Add(self.synthList, 1, wx.EXPAND)

        bsz = wx.BoxSizer(wx.HORIZONTAL)
        bsz.Add(ok, 1, wx.EXPAND)
        bsz.Add(cancel, 1, wx.EXPAND)

        msz = wx.BoxSizer(wx.VERTICAL)
        msz.Add(ssz, 1, wx.EXPAND)
        msz.Add(bsz, 1, wx.EXPAND)
        self.SetSizer(msz)

    def GetData(self):
        pass
