# synthDrivers/UML.py
# Copyright (C) 2022 Yukio Nozawa, ACT Laboratory
# Some code provided by the NVDA community

import config
import synthDriverHandler
from speech.commands import IndexCommand, LangChangeCommand
import queue
import threading
from . import _umlCodes

# On NVDA startup, SynthDriver objects are imported first. If confspec is in UML GlobalPlugin, accessing to the config values seems to make an invalid cache and breaks UML config. Define conficspec here.
confspec = {
    "primaryLanguage": "string(default=ja)",
    "strategy": "string(default=word)",
    "japanese": "string(default=_)",
    "fallback": "string(default=_)",
    "checkForUpdatesOnStartup": "boolean(default=True)",
}
config.conf.spec["UML_global"] = confspec


class InitializationError(Exception):
    pass


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
    default_lang = _umlCodes.JAPANESE

    @classmethod
    def check(cls):
        return True

    def __init__(self):
        self.strategy = "word"
        if "strategy" in config.conf["UML_global"]:
            self.strategy = config.conf["UML_global"]["strategy"]
        self    .primary_lang = "ja"
        if "primaryLanguage" in config.conf["UML_global"]:
            # For some reason, primaryLanguage might be inaccessible on NVDA startup. Still haven't figured out why. Maybe configSpec is not loaded yet?
            self.primary_lang = config.conf["UML_global"]["primaryLanguage"]
        self.last_lang = self.primary_lang
        self.synthIdentifierMap = {
            'en': config.conf["UML_global"]["fallback"],
            'ja': config.conf["UML_global"]["japanese"],
        }

        self.synthInstanceMap = {}
        for k, v in self.synthIdentifierMap.items():
            try:
                synth = synthDriverHandler._getSynthDriver(v)()
                synth.initSettings()
                self.synthInstanceMap[k] = synth
            except BaseException as e:
                raise InitializationError(
                    "Failed to load %s (reason: %s)" % (v, e))
            # end wrap errors on exception
        # end load synth for all languages
        self.cur_synth = None
        self.lock = threading.Lock()
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
        seq = modseq(seq, self.last_lang, self.strategy)
        synth = self.synthInstanceMap[self.last_lang]
        textList = []
        for i, item in enumerate(seq):
            if isinstance(item, LangChangeCommand):
                if item.lang == self.last_lang:
                    continue
                if textList:
                    _execWhenDone(self.wait_speak, synth, textList[:])
                    textList = []
                # end textList exists
                self.last_lang = item.lang
                if item.lang == 'en':
                    synth = self.synthInstanceMap['en']
                else:
                    synth = self.synthInstanceMap['ja']
            # end LangChangeCommand
            elif isinstance(item, IndexCommand):
                textList.append(item)
            elif isinstance(item, str):
                textList.append(item)
        # do the final speaking
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
        try:
            while True:
                item = bgQueue .get_nowait()
                bgQueue .task_done()
        except queue.Empty:
            pass

        for v in self.synthInstanceMap.values():
            v.cancel()
        self.lastindex = None
        self.done.set()

    def on_done(self, synth):
        if synth == self:
            return
        with self.lock:
            if synth == self.cur_synth:
                self.done.set()

    def notify_done(self):
        synthDriverHandler.synthDoneSpeaking.notify(synth=self)

    def on_index(self, synth=None, index=None):
        if synth == self:
            return
        # We dont' care which synth this came from, pass it on
        synthDriverHandler.synthIndexReached.notify(synth=self, index=index)

    @property
    def language(self):
        return self.last_lang


def stringsplit(s, last_lang, strategy):
    """Processes speaking text. Returns a newly generated part of SpeechSequence."""
    return stringsplit_word(s, last_lang) if strategy == "word" else stringsplit_sentence(s, last_lang)


def stringsplit_word(s, last_lang):
    if s.strip() == '':
        return []

    lst = []
    start = 0
    # set kind using the first char
    lastkind = str2kind(s, 0, last_lang)

    for pos, c in enumerate(s):
        u = ord(c)
        if u == 32:
            continue  # spaces don't change anything
        kind = str2kind(s, pos, lastkind)
        if kind != lastkind:  # switched languages
            lst.extend([LangChangeCommand(lastkind), s[start:pos]])
            lastkind = kind
            start = pos
        # end kind is changed?
    # end enumerate
    # The final piece of text that wasn't inserted yet
    lst.extend([LangChangeCommand(kind), s[start:pos+1]])
    return lst


def stringsplit_sentence(s, last_lang):
    if s.strip() == '':
        return []

    lst = []
    start = 0
    found = _umlCodes.ENGLISH

    for pos, c in enumerate(s):
        u = ord(c)
        if u == 32:
            continue  # spaces don't change anything
        kind = char2kind(u)
        if kind != _umlCodes.ENGLISH:
            found = kind
            break
        # end found non-fallback
    # end enumerate
    lst.extend([LangChangeCommand(found), s])
    return lst


def modseq(seq, last_lang, strategy):
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
            newseq.extend(stringsplit(item, last_lang, strategy))
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
        return _umlCodes.JAPANESE
    # end japanese
    # Currently, non-Japanese is considered as English. Add logic when supporting other languages.
    return _umlCodes.ENGLISH


def str2kind(s, idx, lastkind):
    """Returns kind at the specified index of the specified string."""
    char = ord(s[idx])
    if char >= 0x30 and char <= 0x39:
        # Use the last language for numbers
        return lastkind
    return char2kind(ord(s[idx]))
