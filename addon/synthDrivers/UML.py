# synthDrivers/UML.py
# Copyright (C) 2022 Yukio Nozawa, ACT Laboratory
# Some code provided by the NVDA community

import synthDriverHandler
from synthDriverHandler import SynthDriver, synthIndexReached, synthDoneSpeaking
from speech.commands import IndexCommand, LangChangeCommand
import queue
import threading

SYNTH1 = 'espeak'
SYNTH2 = 'HISS'

bgQueue = queue.Queue()
class BgThread(threading.Thread):
	def __init__(self):
		super().__init__(name=f"{self.__class__.__module__}.{self.__class__.__qualname__}")
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

class SynthDriver(SynthDriver):
	name = 'UML'
	description = 'Universal multilingual'
	supportedSettings = ()
	supportedCommands = {IndexCommand,}
	supportedNotifications = {synthIndexReached, synthDoneSpeaking}

	@classmethod
	def check(cls):
		synth1 = synthDriverHandler._getSynthDriver(SYNTH1)
		synth2 = synthDriverHandler._getSynthDriver(SYNTH2)
		return True

	def __init__(self):
		self.synth1 = synthDriverHandler._getSynthDriver(SYNTH1)()
		self.synth1.initSettings()
		self.synth2 = synthDriverHandler._getSynthDriver(SYNTH2)()
		self.synth2.initSettings()
		self.cur_synth = None
		self.lock = threading.Lock()
		self.last_lang = 'en'
		self.lastindex = None
		synthDoneSpeaking.register(self.on_done)
		synthIndexReached.register(self.on_index)
		self.done = threading.Event()
		self.thread = BgThread()
		self.thread.daemon = True
		self.thread.start()

	def terminate(self):
		self.synth1.terminate()
		self.synth2.terminate()
		synthDoneSpeaking.unregister(self.on_done)
		synthIndexReached.unregister(self.on_index)
		bgQueue.put((None, None, None))
		self.thread.join()

	def speak(self, seq):
		print(f"before speaking {seq}")
		seq = modseq(seq, 'en')
		print(f"speaking {seq}")
		synth = self.synth1
		textList = []
		lastindex = None
		for i, item in enumerate(seq):
			if isinstance(item, LangChangeCommand):
				if item.lang == self.last_lang: continue
				if textList:
					if lastindex:
						textList.append(IndexCommand(lastindex))
						lastindex = None
					_execWhenDone(self.wait_speak, synth, textList[:])
					textList = []
				self.last_lang = item.lang
				if item.lang == 'en':
					synth = self.synth1
				else:
					synth = self.synth2
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

		self.synth1.cancel()
		self.synth2.cancel()
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
		synthDoneSpeaking.notify(synth=self)

	def on_index(self, synth=None, index=None):
		if synth == self:
			return
		print(f"on_index: {index} {synth}")
		# We dont' care which synth this came from, pass it on
		synthIndexReached.notify(synth=self, index=index)

	@property
	def language(self):
		return self.last_lang

def stringsplit(s, lang):
	if s.strip() == '': return []
	kinds = (LangChangeCommand(lang), LangChangeCommand('ja'))
	def kind_of(u):
		"""Returns kind of character, which is represented by a unicode codepoint. 0 for english, 1 for japanese."""
		if (u >= 0x3000 and u <= 0x30ff) or (u >= 0x4e00 and u <= 0x9fbf) or (u >= 0xff00 and u <= 0xffef) or (u >= 0x2160 and u <= 0x2169): return 1
		return 0
	lst = []
	lastkind = 0
	start = 0
	#If lastkind is not set correctly here, the first entry will be blank.
	lastkind = kind_of(ord(s[0]))

	for pos, c in enumerate(s):
		u = ord(c)
		if u == 32: continue #spaces don't change anything
		kind = kind_of(u)
		if kind != lastkind: #switched languages
			lst.extend([kinds[lastkind], s[start:pos]])
			lastkind = kind
			start = pos

	#The final piece of text that wasn't inserted yet
	lst.extend([kinds[kind], s[start:pos+1]])
	return lst

def modseq(seq, lang):
	"""NVDA's LangChangeCommand only refers markup information like html lang attribute. We want more dynamic change. Process the input sequence and insert LangChangeCommand here."""
	newseq = []
	for i, item in enumerate(seq):
		if isinstance(item, IndexCommand) and len(seq)-1 > i and isinstance(seq[i+1], IndexCommand):
			continue
		if isinstance(item, LangChangeCommand):
			continue
		if isinstance(item, str):
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