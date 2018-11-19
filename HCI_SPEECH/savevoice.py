# coding=utf-8
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class SaveVoice(QObject):
    """docstring for SaveVoice"""

    save_finished = pyqtSignal()

    def __init__(self):
        super(SaveVoice, self).__init__()
        self.initialParams()

    def initialParams(self):
        self.txt = None
        # name by timestamp
        self.save_name = None
        # type => inital 'Ting-Ting'
        self.voice_type = 'Ting-Ting'
        # rate => [0 ~ 200]
        self.voice_rate = 200
        # volume => [0, 2]
        self.voice_volume = 1

    def call_sys_say(self, voice_type, voice_rate, save_name, txt):
        # call system saying
        os_str = 'say' + ' -r ' + str(voice_rate) + ' -v ' + str(voice_type) + \
            ' -o ./records/' + str(save_name) + ' ' + str(txt)
        os.system(os_str)

    def start_save(self):
        self.call_sys_say(self.voice_type, self.voice_rate, self.save_name, self.txt)
        self.save_finished.emit()

    def set_voice_rate(self, rate):
        self.voice_rate = rate

    def set_voice_name(self, name):
        name = self.predeal_word(name, '_')
        self.save_name = name[:5] if len(name) >= 5 else name

    def set_voice_type(self, v_type):
        self.voice_type = v_type

    def set_txt(self, txt):
        self.txt = self.predeal_word(txt, ' ')

    def predeal_word(self, txt, r_word):
        # change the encoding type of string
        '''
                encode => unicode(str) => type 可被识别的
        '''
        return txt.encode('utf-8', 'ignore').decode().replace('\n', r_word).replace('\t', r_word)
