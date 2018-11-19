import pyttsx3
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# engine = pyttsx3.init()
# rate = engine.getProperty('rate')
# # rate: [100~ 700] 100: 0.5, 150: 0.75 200: 1 250: 1.25 300: 1.5 350: 1.75 400: 2
# # volume: [0 ~ 2] => 0 ~ 20 / 10
# engine.setProperty('voice', 'com.apple.speech.synthesis.voice.mei-jia')
# voices = engine.getProperty('voices')
# for item in voices:
#     print(item)
# engine.say('你好')
# engine.runAndWait()


class Speecher(QObject):
    """docstring for Speecher"""

    finished = pyqtSignal()
    word_read = pyqtSignal(dict)

    def __init__(self):
        super(Speecher, self).__init__()
        self.engine = pyttsx3.init()
        self.build_connection()
        self.init_reading_state()

    def build_connection(self):
        self.engine.connect('started-utterance', self.on_start)
        self.engine.connect('started-word', self.on_word)
        self.engine.connect('finished-utterance', self.on_end)

    def init_reading_state(self):
        # The label of reading state
        self.reading = False
        # A label of reading finished
        self.reading_finished = False
        # The voice rate initial
        self.__voice_rate = 200
        # The voice volume inital [0, 1]
        self.__voice_volume = 0.5
        # The voice type initial
        self.__voice_type = None

        self.engine.setProperty('volume', self.__voice_volume)
        self.engine.setProperty('rate', self.__voice_rate)

    def get_type_voices(self, type):
        '''
                type: zn or en we want to elect voice
        '''
        voices = dict()
        if type == 'z_n':
            for item in self.engine.getProperty('voices'):
                if item.languages[0][:2] == 'zh':
                    voices[item.id] = 'Name: ' + item.name + '. Language: ' + item.languages[0] + '. Age: ' + item.age

        elif type == 'e_n':
            for item in self.engine.getProperty('voices'):
                if item.languages[0][:2] == 'en':
                    voices[item.id] = 'Name: ' + str(item.name) + '. Language: ' + \
                        str(item.languages[0]) + '. Age: ' + str(item.age)
        elif type == 'j_p':
            for item in self.engine.getProperty('voices'):
                if item.languages[0][:2] == 'ja':
                    voices[item.id] = 'Name: ' + str(item.name) + '. Language: ' + \
                        str(item.languages[0]) + '. Age: ' + str(item.age)
        return voices

    def set_voice_rate(self, delta_rate):
        rate = self.__voice_rate + delta_rate
        if rate > 400 or rate < 100:
            return
        self.__voice_rate += delta_rate

    def set_voice_volume(self, volume):
        self.__voice_volume = volume / 10

    def set_voice_type(self, type):
        self.__voice_type = type

    def get_voice_rate(self):
        return 'Speed: ×' + str(self.__voice_rate / 200)

    def get_voice_type(self):
        return self.__voice_type.split('.')[-2] if self.__voice_type.split('.')[-1] == 'premium' else self.__voice_type.split('.')[-1]

    def get_txt(self):
        return self.txt

    def get_rate(self):
        return self.__voice_rate

    def on_start(self, name):
        '''
            Deal when start a loop
        '''
        # QApplication.processEvents()
        self.reading = True

    def on_word(self, name, location, length):
        '''
            Deal when in loop
        '''
        # QApplication.processEvents()
        self.word_read.emit({'location': location, 'length': length})

    def on_end(self, name, completed):
        '''25
            Deal when loop ending
        '''
        self.reading = False
        self.reading_finished = True
        self.finished.emit()
        self.engine.stop()
        # thread is over

    def start_reading(self):
        # thread always exists
        # keep thread running so that main thread will not stop
        self.reading_finished = False
        self.engine.setProperty('rate', self.__voice_rate)
        self.engine.setProperty('volume', self.__voice_volume)
        self.engine.setProperty('voice', self.__voice_type)
        self.engine.say(self.txt)
        self.engine.startLoop()

    def set_reading_txt(self, txt):
        self.txt = txt

    def pause_reading_loop(self):
        self.reading_finished = True
        self.reading = False
        self.finished.emit()
        self.engine.stop()

    def get_reading_state(self):
        return self.reading

    def is_reading_finished(self):
        return self.reading_finished

    def set_reading_finished(self, state):
        self.reading_finished = state
