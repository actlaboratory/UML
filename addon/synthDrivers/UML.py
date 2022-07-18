# synthDrivers/UML.py
# Copyright (C) 2022 Yukio Nozawa, ACT Laboratory
# Some code provided by the NVDA community

import synthDriverHandler
from speech.commands import IndexCommand, LangChangeCommand
import queue
import threading
from . import _umlLanguages

SYNTH1 = 'espeak'
SYNTH2 = 'HISS'

synthIdentifierMap = {
    'en': 'espeak',
    'ja': 'HISS',
}

bgQueue = queue.Queue()


class BgThread(threading.Thread):
    def __init__(self):
        super().__init__(
            name=f"{self.__class__.__module__}.{self.__class__.__qualname__}")
        self.setDaemon(True)

    def run(self):
        global isSpeaking
        while True:
            func, args, kwargs = bgQueue.get()
            if not func:
                break
            try:
                func(*args, **kwargs)
            except:
                log.error("Error running function from queue", exc_info=True)
            bgQueue.task_done()


def _execWhenDone(func, *args, mustBeAsync=True, **kwargs):
    global bgQueue
    if mustBeAsync or bgQueue.unfinished_tasks != 0:
        # Either this operation must be asynchronous or There is still an operation in progress.
        # Therefore, run this asynchronously in the background thread.
        bgQueue.put((func, args, kwargs))
    else:
        func(*args, **kwargs)


class SynthDriver(synthDriverHandler.SynthDriver):
    name = 'UML'
    description = 'Universal multilingual'
    supportedSettings = ()
    supportedCommands = {IndexCommand, }
    supportedNotifications = {
        synthDriverHandler.synthIndexReached, synthDriverHandler.synthDoneSpeaking
    }

    @classmethod
    def check(cls):
        return True

    def __init__(self):
        self.synthInstanceMap = {}
        for k, v in synthIdentifierMap.items():
            synth = synthDriverHandler._getSynthDriver(v)()
            synth.initSettings()
            self.synthInstanceMap[k] = synth
        # end load synth for all languages
        self.cur_synth = None
        self.lock = threading.Lock()
        self.last_lang = ''
        self.lastindex = None
        synthDriverHandler.synthDoneSpeaking.register(self.on_done)
        synthDriverHandler.synthIndexReached.register(self.on_index)
        self.done = threading.Event()
        self.thread = BgThread()
        self.thread.daemon = True
        self.thread.start()

    def terminate(self):
        for v in self.synthInstanceMap.values():
            v.terminate()
        synthDriverHandler.synthDoneSpeaking.unregister(self.on_done)
        synthDriverHandler.synthIndexReached.unregister(self.on_index)
        bgQueue.put((None, None, None))
        self.thread.join()

    def speak(self, seq):
        seq = modseq(seq, 'en')
        print("seq: %s" % seq)
        synth = self.synthInstanceMap[self.last_lang]
        textList = []
        lastindex = None
        for i, item in enumerate(seq):
            print("item: %s" % item)
            if isinstance(item, LangChangeCommand):
                if item.lang == self.last_lang:
                    print("same synth, skipping")
                    continue
                if textList:
                    print("textlist exists")
                    if lastindex:
                        print("lastIndex exists")
                        textList.append(IndexCommand(lastindex))
                        lastindex = None
                    # end lastIndex exists
                    print("speakWait")
                    _execWhenDone(self.wait_speak, synth, textList[:])
                    textList = []
                # end textList exists
                self.last_lang = item.lang
                print("switching language")
                if item.lang == 'en':
                    synth = self.synthInstanceMap['en']
                    print("english selected")
                else:
                    synth = self.synthInstanceMap['ja']
                    print("japanese selected")
            # end LangChangeCommand
            elif isinstance(item, IndexCommand):
                lastindex = item.index
            elif isinstance(item, str):
                textList.append(item)
        # do the final speaking
        if lastindex:
            textList.append(IndexCommand(lastindex))
        if textList:
            _execWhenDone(self.wait_speak, synth, textList[:])
            textList = []
        _execWhenDone(self.notify_done)

    def wait_speak(self, synth, seq):
        with self.lock:
            self.done.clear()
            self.cur_synth = synth
            synth.speak(seq)
        self.done.wait()

    def cancel(self):
        print("cancel")
        try:
            while True:
                item = bgQueue .get_nowait()
                bgQueue .task_done()
        except queue.Empty:
            pass

        for v in self.synthInstanceMap.values():
            v.cancel()
        self.lastindex = None
        self.last_lang = 'en'
        self.done.set()
        print("cancelled")

    def on_done(self, synth):
        if synth == self:
            return
        with self.lock:
            print(f"Done: {synth}")
            if synth == self.cur_synth:
                self.done.set()

    def notify_done(self):
        synthDriverHandler.synthDoneSpeaking.notify(synth=self)

    def on_index(self, synth=None, index=None):
        if synth == self:
            return
        print(f"on_index: {index} {synth}")
        # We dont' care which synth this came from, pass it on
        synthDriverHandler.synthIndexReached.notify(synth=self, index=index)

    @property
    def language(self):
        return self.last_lang


def stringsplit(s, lang):
    """Processes speaking text. Returns a newly generated part of SpeechSequence."""
    if s.strip() == '':
        return []

    lst = []
    start = 0
    # set kind using the first char
    lastkind = str2kind(s, 0)

    for pos, c in enumerate(s):
        u = ord(c)
        if u == 32:
            continue  # spaces don't change anything
        kind = str2kind(s, pos)
        if kind != lastkind:  # switched languages
            lst.extend([LangChangeCommand(_umlLanguages.langCodeMap[lastkind]), s[start:pos]])
            lastkind = kind
            start = pos
        # end kind is changed?
    # end enumerate
    # The final piece of text that wasn't inserted yet
    lst.extend([LangChangeCommand(_umlLanguages.langCodeMap[kind]), s[start:pos+1]])
    return lst


def modseq(seq, lang):
    """NVDA's LangChangeCommand only refers markup information like html lang attribute. We want more dynamic change. Process the input sequence and insert LangChangeCommand here."""
    newseq = []
    for i, item in enumerate(seq):
        if isinstance(item, IndexCommand) and len(seq)-1 > i and isinstance(seq[i+1], IndexCommand):
            # Continuous IndexCommand should be ignored.
            continue
        if isinstance(item, LangChangeCommand):
            # Prioritize original LangChangeCommand
            continue
        if isinstance(item, str):
            # Convert some chars which some Japanese synths cannot read properly
            item = item.translate(jpn_translate)
            newseq.extend(stringsplit(item, lang))
        else:
            newseq.append(item)
    return newseq


jpn_translate = {
    0x2170: 0x2160,
    0x2171: 0x2161,
    0x2172: 0x2162,
    0x2173: 0x2163,
    0x2174: 0x2164,
    0x2175: 0x2165,
    0x2176: 0x2166,
    0x2177: 0x2167,
    0x2178: 0x2168,
    0x2179: 0x2169,
}


def char2kind(u):
    """Returns kind of character, which is represented by a unicode codepoint. Used as an internal function from str2kind."""
    if (u >= 0x3000 and u <= 0x30ff) or (u >= 0x4e00 and u <= 0x9fbf) or (u >= 0xff00 and u <= 0xffef) or (u >= 0x2160 and u <= 0x2169):
        return _umlLanguages.JAPANESE
    # end japanese
    # Currently, non-Japanese is considered as English. Add logic when supporting other languages.
    return _umlLanguages.ENGLISH


def str2kind(s, idx):
    """Returns kind at the specified index of the specified string."""
    return char2kind(ord(s[idx]))
