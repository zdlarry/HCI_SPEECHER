# coding=utf-8
import sys
import numpy as np
import copy
from PyQt5.QtOpenGL import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import threading
from speecher import Speecher
from voicetimer import VoiceTimer
from savevoice import SaveVoice


class LoadingDialog(QWidget):
    """docstring for LoadingDialog"""

    def __init__(self):
        super(LoadingDialog, self).__init__()

        self.initParams()
        self.arrangeLayout()

        self.setWindowOpacity(0.7)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setFixedSize(QSize(160, 120))

        self.setStyle()

    def initParams(self):
        self.label = QLabel('Loading...', self)
        self.label.setFixedSize(QSize(160, 120))
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def arrangeLayout(self):
        self.hbox = QHBoxLayout()
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.addWidget(self.label, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.setLayout(self.hbox)

    def setPosition(self, posx, posy):
        self.move(posx, posy)

    def setStyle(self):
        self.setStyleSheet(
            'QWidget{border-image: url(./imgs/loading_dialog.png); width: 160px; height: 120px;}')

        self.label.setStyleSheet(
            'QLabel{font-family: "raleway_300"; font-size: 15px; color: white}')


class SliderWidget(QWidget):
    """docstring for SliderWidget"""

    def __init__(self, max, min, value):
        super(SliderWidget, self).__init__()
        self.max = max
        self.min = min
        self.value = value
        self.installEventFilter(self)
        # self.setFixedSize(QSize(70, 85))

        self.setWindowOpacity(1)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.hbox = QHBoxLayout()
        self.hbox.setContentsMargins(0, 10, 0, 10)

        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Vertical)
        self.slider.setRange(self.min, self.max)
        self.slider.setValue(self.value)
        self.slider.setEnabled(True)

        self.hbox.addWidget(self.slider, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.setLayout(self.hbox)

        self.setStyle()

    def setStyle(self):
        self.setStyleSheet(
            'QWidget{border-image: url(./imgs/voicewidget.png); width: 40px; height: 87px}')

        self.slider.setStyleSheet(
            'QSlider::groove:vertical{width: 3px; height: 65px; background: rgb(230, 230, 230);\
                                      border: 0.5px solid rgb(230, 230, 230); \
                                      border-radius: 10px;\
                                      padding: -1px -1px -1px -1px}'
            'QSlider::handle:vertical{height: 5px; width: 6px;\
                                      background: rgb(45, 185, 105);\
                                      margin: -1px -2px -1px -2px; \
                                      border: 1px solid rgb(45, 185, 105); \
                                      border-radius: 3px}'
            'QSlider::add-page:vertical{width: 3px; background: rgb(45, 185, 105); \
                                        border: 0.5px solid rgb(45, 185, 105); \
                                        border-radius: 5px;}')

    def setPosition(self, posx, posy):
        self.move(posx, posy)

    def eventFilter(self, obj, e):
        if QEvent.WindowDeactivate == e.type():
            self.hide()
            return QWidget.eventFilter(self, obj, e)
        else:
            return QWidget.eventFilter(self, obj, e)


class MainWidget(QWidget):
    """docstring for MainWidget"""

    def __init__(self):
        super(MainWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Speech System')
        self.setFixedSize(QSize(360, 490))
        self.center()

        # load modules
        self.loadModules()
        # load font family
        self.loadFontFamily()
        # Add buttons
        self.addPushButtons()
        # add pixmap
        self.addPixmaps()
        # Add text input
        self.addTextEdits()
        # # Add QCombox
        self.addComboxs()
        # # Add Lables
        self.addLabels()

        # set btns style
        self.setBtnsStyle()
        # Set Layout
        self.arrangeLayout()

        self.show()

    def loadModules(self):
        self.speecher = Speecher()
        # when speecher finish a reading => icon change to play
        self.speecher.finished.connect(self.stop_voice_thread)
        # when reading a word => show the underline of txt
        self.speecher.word_read.connect(self.on_word_text)

        # load timer
        self.voicetimer = VoiceTimer()
        # when timer_update, update time label
        self.voicetimer.timer_update.connect(self.update_timer)

        # load saver thread
        self.voice_saver = SaveVoice()
        self.voice_saver.save_finished.connect(self.close_dialog)

        # QWidget load:
        self.loading_dialog = LoadingDialog()

        self.sliderWidget = SliderWidget(20, 0, 10)
        self.sliderWidget.slider.valueChanged[int].connect(self.changeVolume)

    def loadFontFamily(self):
        QFontDatabase.addApplicationFont('fonts/raleway_300.ttf')

    def addPushButtons(self):

        # deal Voice
        self.play = QPushButton(self)
        self.play.clicked.connect(lambda: self.handleVoice('play_or_pause'))

        # self.pause = QPushButton(self)
        # self.pause.clicked.connect(lambda: self.handleVoice('pause'))

        self.faster = QPushButton(self)
        self.faster.clicked.connect(lambda: self.handleVoice('faster'))

        self.slower = QPushButton(self)
        self.slower.clicked.connect(lambda: self.handleVoice('slower'))

        self.setVolume = QPushButton(self)
        self.setVolume.clicked.connect(self.showVolumePanel)

        # deal Lang
        self.Z_N = QPushButton('ZN', self)
        self.E_N = QPushButton('EN', self)
        self.J_P = QPushButton('JP', self)
        self.Z_N.clicked.connect(lambda: self.handleLanguage('z_n'))
        self.E_N.clicked.connect(lambda: self.handleLanguage('e_n'))
        self.J_P.clicked.connect(lambda: self.handleLanguage('j_p'))

        # deal text input
        self.clear_txt = QPushButton(self)
        self.clear_txt.clicked.connect(lambda: self.setText(''))

        # btn to upload voice file
        self.upload_btn = QPushButton('Upload', self)
        self.upload_btn.clicked.connect(lambda: self.handleVoiceFile('upload'))

        # btn to save voice file
        self.save_to_file = QPushButton('Save As File', self)
        self.save_to_file.clicked.connect(lambda: self.handleVoiceFile('save'))

        # btn to show voice type
        self.voice_type_btn = QPushButton(self)
        self.voice_type_btn.setDisabled(True)

    def setBtnsStyle(self):

        self.play.setStyleSheet(
            'QPushButton{border-image: url(./imgs/play_.png); width: 40; height: 40}'
            'QPushButton:hover{border-image: url(./imgs/play_hover.png); width: 40; height: 40}')
        self.faster.setStyleSheet(
            'QPushButton{border-image: url(./imgs/faster_.png); width: 30; height: 30}'
            'QPushButton:hover{border-image: url(./imgs/faster_hover.png); width: 30; height: 30}')
        self.slower.setStyleSheet(
            'QPushButton{border-image: url(./imgs/slower_.png); width: 30; height: 30}'
            'QPushButton:hover{border-image: url(./imgs/slower_hover.png); width: 30; height: 30}')
        self.clear_txt.setStyleSheet(
            'QPushButton{border-image: url(./imgs/flush_.png); width: 20; height: 20}'
            'QPushButton:hover{border-image: url(./imgs/flush_hover.png); width: 20; height: 20}')
        self.setVolume.setStyleSheet(
            'QPushButton{border-image: url(./imgs/voice_.png); width: 16; height: 16}'
            'QPushButton:hover{border-image: url(./imgs/voice_hover.png); width: 16; height: 16}')
        self.voice_type_btn.setStyleSheet(
            'QPushButton{border-image: url(./imgs/type.png); width: 25; height: 25}')
        self.save_to_file.setStyleSheet(
            'QPushButton{font-size: 11px; font-family: "raleway_300"; border:0.5px solid rgba(0, 198, 216, 1); color: rgba(0, 198, 216, 1)}'
            'QPushButton::hover{border:0.5px solid rgba(20, 228, 246, 1); color: rgba(20, 228, 246, 1)}')
        self.upload_btn.setStyleSheet(
            'QPushButton{font-size: 11px; font-family: "raleway_300"; border:0.5px solid gray;}'
            'QPushButton::hover{border:0.5px solid rgba(0, 158, 176, 1); color: rgba(0, 158, 176, 1)}')
        self.handleLanguage('z_n')
        self.play.setCheckable(True)
        self.play.setCursor(Qt.PointingHandCursor)
        self.faster.setCursor(Qt.PointingHandCursor)
        self.slower.setCursor(Qt.PointingHandCursor)
        self.setVolume.setCursor(Qt.PointingHandCursor)
        self.clear_txt.setCursor(Qt.PointingHandCursor)
        self.save_to_file.setFixedSize(QSize(90, 20))
        self.save_to_file.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setFixedSize(QSize(80, 20))
        self.E_N.setFixedSize(QSize(25, 25))
        self.E_N.setCursor(Qt.PointingHandCursor)
        self.Z_N.setFixedSize(QSize(25, 25))
        self.Z_N.setCursor(Qt.PointingHandCursor)
        self.J_P.setFixedSize(QSize(25, 25))
        self.J_P.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setCursor(Qt.PointingHandCursor)

    def addTextEdits(self):
        # The main text input edit
        self.textEdit = QTextEdit(self)
        # forbid richtext format
        self.textEdit.setAcceptRichText(False)
        # when text changed, changed the word size by the length of txt
        self.textEdit.textChanged.connect(self.on_text_changed)
        self.textEdit.setPlaceholderText('Please input the voice text here...')
        self.textEdit.setStyleSheet(
            'QTextEdit{font-size: 15px; font-family: "raleway_300"; border:none; color: black}')

    def getTextEditContain(self):
        return self.textEdit.toPlainText()

    def addComboxs(self):
        # Add QComboxes into panel to select voice type
        self.voiceTypeCombox = QComboBox(self)
        self.voiceTypeCombox.setView(QListView(self))
        self.voiceTypeCombox.setLineEdit(QLineEdit())
        self.voiceTypeCombox.lineEdit().setText('select the type of voice...')
        self.voiceTypeCombox.lineEdit().setReadOnly(True)
        self.voiceTypeCombox.setStyleSheet(
            'QComboBox {font-family: "raleway_300"; height: 25px; border-radius: 8px; font-size: 12px; padding-left: 10px}'
            "QComboBox::drop-down {width: 30 px; border: 0px; height: 25px}"
            'QComboBox::down-arrow {border-image: url(./imgs/arrow.png); height: 18px; width: 18px}')
        self.voiceTypeCombox.view().setStyleSheet(
            "QListView {font-family: 'raleway_300'; font-size: 10px; outline: 0px; border: none}"
            "QListView::item {padding: 5px 3x 3px 3px; border-width: 0px; border-radius: 5px}"
            "QListView::item:selected {background-color: rgba(0, 198, 216, 1);}")
        self.voiceTypeCombox.setCursor(Qt.PointingHandCursor)
        self.voiceTypeCombox.activated[str].connect(self.changeVoice)

    def addLabels(self):
        # label to show play time
        self.voice_play_time = QLabel(self)
        self.voice_play_time.setStyleSheet(
            'QLabel{font-family: "raleway_300"; font-size: 20px; color: white}')
        time = self.voicetimer.get_initial_time()
        self.voice_play_time.setText(time)

        # label to show type of voice
        self.voice_file_name = QLabel(self)
        self.voice_file_name.setText('Click btn to upload voice file...')

        # label to set up wave png
        self.wave_label = QLabel(self)
        self.wave_label.setFixedSize(self.width(), 40)
        # pixmap fit the size of label =>> setScaledContents(True)
        self.wave_label.setScaledContents(True)
        self.wave_label.setPixmap(self.wave_pixmap)

        self.speed_label = QLabel(self)
        self.speed_label.setText(self.speecher.get_voice_rate())
        self.speed_label.setStyleSheet(
            'QLabel{font-family: "raleway_300"; font-size: 12px;}')

    def addPixmaps(self):
        self.wave_pixmap = QPixmap('./imgs/wave.png')

    def arrangeLayout(self):
        # set layout
        self.global_vbox = QVBoxLayout()
        self.title_vbox = QVBoxLayout()
        self.text_grid_box = QGridLayout()
        self.voice_handler_hbox = QHBoxLayout()
        self.voice_type_select_hbox = QHBoxLayout()
        self.upload_hbox = QHBoxLayout()

        # set title layout
        tmp_widget = QWidget(self)
        tmp_widget.setStyleSheet(
            'QWidget{background-color: rgba(0, 158, 176, 1)}')
        tmp_vbox = QVBoxLayout()
        self.title_vbox.setContentsMargins(0, 0, 0, 0)
        self.title_vbox.setSpacing(0)
        self.title_vbox.addWidget(tmp_widget)
        tmp_widget.setLayout(tmp_vbox)
        tmp_vbox.addStretch(3)
        tmp_vbox.addWidget(self.voice_play_time, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        tmp_vbox.addWidget(self.save_to_file, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        tmp_vbox.addStretch(2)
        self.title_vbox.addWidget(self.wave_label)
        self.voice_type_select_hbox.setStretch(0, 2)
        self.voice_type_select_hbox.setStretch(1, 1)
        self.voice_type_select_hbox.setStretch(2, 1)

        # set textEdit layout
        self.text_grid_box.setContentsMargins(10, 0, 15, 0)
        self.text_grid_box.setSpacing(7)
        self.text_grid_box.addWidget(self.Z_N, 0, 0)
        self.text_grid_box.addWidget(self.E_N, 1, 0)
        self.text_grid_box.addWidget(self.J_P, 2, 0)
        self.text_grid_box.addWidget(self.textEdit, 0, 1, 4, 1)

        # set voice handler btns
        # self.voice_handler_hbox.addStretch(1)
        self.voice_handler_hbox.setContentsMargins(10, 0, 10, 0)
        self.voice_handler_hbox.addStretch(1)
        self.voice_handler_hbox.addWidget(self.clear_txt, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.voice_handler_hbox.addWidget(self.slower, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.voice_handler_hbox.addWidget(self.play, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.voice_handler_hbox.addWidget(self.faster, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.voice_handler_hbox.addWidget(self.setVolume, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.voice_handler_hbox.addStretch(1)

        # set voice type select combox
        self.voice_type_select_hbox.setContentsMargins(10, 0, 10, 0)
        self.voice_type_select_hbox.setSpacing(5)
        self.voice_type_select_hbox.addWidget(self.voice_type_btn)
        self.voice_type_select_hbox.addWidget(self.voiceTypeCombox)
        self.voice_type_select_hbox.setStretch(0, 0.5)
        self.voice_type_select_hbox.setStretch(1, 5)

        # set upload file layout
        self.upload_hbox.setContentsMargins(10, 0, 10, 10)
        self.upload_hbox.addWidget(self.voice_file_name, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.upload_hbox.addWidget(self.upload_btn)
        self.upload_hbox.setStretch(0, 5)
        self.upload_hbox.setStretch(1, 1)

        # add global layout
        self.global_vbox.setContentsMargins(0, 0, 0, 0)
        self.global_vbox.addLayout(self.title_vbox)
        self.global_vbox.addLayout(self.text_grid_box)
        self.global_vbox.addLayout(self.voice_handler_hbox)
        self.global_vbox.addWidget(self.speed_label, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        self.global_vbox.addLayout(self.voice_type_select_hbox)
        self.global_vbox.addLayout(self.upload_hbox)
        self.global_vbox.setStretch(0, 2)
        self.global_vbox.setStretch(1, 3)

        self.setLayout(self.global_vbox)

    def changeVoiceType(self, type):
        # Select voice of Z_N initial
        self.voiceTypeCombox.clear()
        self.type_voices = self.speecher.get_type_voices(type)
        for item in self.type_voices.values():
            self.voiceTypeCombox.addItem(item)
        self.changeVoice(list(self.type_voices.values())[0])

    def handleVoice(self, type):
        if type == 'play_or_pause':
            if not self.speecher.get_reading_state():
                if self.getTextEditContain() == '':
                    return
                self.play.setStyleSheet(
                    'QPushButton{border-image: url(./imgs/pause_.png); width: 40; height: 40}'
                    'QPushButton:hover{border-image: url(./imgs/pause_hover.png); width: 40; height: 40}')
                # speecher set text container
                self.speecher.set_reading_txt(self.getTextEditContain())
                # # a thread for speecher reading
                voice_thread = threading.Thread(target=self.speecher.start_reading)
                voice_thread.start()

                # start reading timer
                self.update_timer(self.voicetimer.get_initial_time())
                self.voicetimer.start_timer()

            else:
                self.speecher.pause_reading_loop()

        elif type == 'faster':
            print('faster')
            self.speecher.set_voice_rate(50)
            self.speed_label.setText(self.speecher.get_voice_rate())
        elif type == 'slower':
            print('slower')
            self.speecher.set_voice_rate(-50)
            self.speed_label.setText(self.speecher.get_voice_rate())

    def stop_voice_thread(self):
        self.play.setStyleSheet(
            'QPushButton{border-image: url(./imgs/play_.png); width: 40; height: 40}'
            'QPushButton:hover{border-image: url(./imgs/play_hover.png); width: 40; height: 40}')
        self.textEdit.selectAll()
        self.textEdit.setTextColor(Qt.black)

        # clear Cursor
        text_edit_cursor = self.textEdit.textCursor()
        text_edit_cursor.movePosition(QTextCursor.Start)
        self.textEdit.setTextCursor(text_edit_cursor)
        self.textEdit.clearFocus()

        self.voicetimer.stop_timer()

    def handleLanguage(self, type):
        self.changeVoiceType(type)
        if type == 'z_n':
            self.Z_N.setStyleSheet(
                'QPushButton{font-size: 10px; font-family: "raleway_300"; border:0.7px solid rgba(0, 198, 216, 1);border-radius:12px; background-color: rgba(0, 198, 216, 1); color: white}'
                'QPushButton::hover{background-color: rgba(0, 218, 236, 1); color: white}')
            self.E_N.setStyleSheet(
                'QPushButton{font-size: 10px; font-family: "raleway_300"; border:0.7px solid rgba(0, 198, 216, 1);border-radius:12px; color:rgba(0, 198, 216, 1)}'
                'QPushButton::hover{background-color: rgba(0, 218, 236, 1); color: white}')
            self.J_P.setStyleSheet(
                'QPushButton{font-size: 10px; font-family: "raleway_300"; border:0.7px solid rgba(0, 198, 216, 1);border-radius:12px; color:rgba(0, 198, 216, 1)}'
                'QPushButton::hover{background-color: rgba(0, 218, 236, 1); color: white}')
        elif type == 'e_n':
            self.Z_N.setStyleSheet(
                'QPushButton{font-size: 10px; font-family: "raleway_300"; border:0.7px solid rgba(0, 198, 216, 1);border-radius:12px; color: rgba(0, 198, 216, 1)}'
                'QPushButton::hover{background-color: rgba(0, 218, 236, 1); color: white}')
            self.E_N.setStyleSheet(
                'QPushButton{font-size: 10px; font-family: "raleway_300"; border:0.7px solid rgba(0, 198, 216, 1);border-radius:12px; background-color: rgba(0, 198, 216, 1); color: white}'
                'QPushButton::hover{background-color: rgba(0, 218, 236, 1); color: white}')
            self.J_P.setStyleSheet(
                'QPushButton{font-size: 10px; font-family: "raleway_300"; border:0.7px solid rgba(0, 198, 216, 1);border-radius:12px; color: rgba(0, 198, 216, 1)}'
                'QPushButton::hover{background-color: rgba(0, 218, 236, 1); color: white}')
        else:
            self.Z_N.setStyleSheet(
                'QPushButton{font-size: 10px; font-family: "raleway_300"; border:0.7px solid rgba(0, 198, 216, 1);border-radius:12px; color: rgba(0, 198, 216, 1)}'
                'QPushButton::hover{background-color: rgba(0, 218, 236, 1); color: white}')
            self.J_P.setStyleSheet(
                'QPushButton{font-size: 10px; font-family: "raleway_300"; border:0.7px solid rgba(0, 198, 216, 1);border-radius:12px; background-color: rgba(0, 198, 216, 1); color: white}'
                'QPushButton::hover{background-color: rgba(0, 218, 236, 1); color: white}')
            self.E_N.setStyleSheet(
                'QPushButton{font-size: 10px; font-family: "raleway_300"; border:0.7px solid rgba(0, 198, 216, 1);border-radius:12px; color: rgba(0, 198, 216, 1)}'
                'QPushButton::hover{background-color: rgba(0, 218, 236, 1); color: white}')

    def setText(self, txt):
        # stop the thread and clear timer
        self.speecher.pause_reading_loop()
        self.voicetimer.stop_timer()
        self.update_timer(self.voicetimer.get_initial_time())

        self.textEdit.setPlainText(txt)
        self.speecher.set_reading_finished(False)
        # self.textEdit.setHtml('<span style=" color:#ff0000;">红色</span>')

    @pyqtSlot(str)
    def update_timer(self, time_label):
        self.voice_play_time.setText(time_label)

    @pyqtSlot(dict)
    def on_word_text(self, txt_info):
        # format the style of text
        self.textEdit.selectAll()
        self.textEdit.setTextColor(Qt.gray)
        # get word location and the length of word
        word_start = txt_info['location']
        word_length = txt_info['length']
        # start a cursor of text
        text_edit_cursor = self.textEdit.textCursor()
        text_edit_cursor.movePosition(QTextCursor.Start)
        self.textEdit.setTextCursor(text_edit_cursor)

        self.textEdit.clearFocus()
        for index in np.arange(word_length):
            # set txt to that posistion
            text_edit_cursor.setPosition(word_start + index)
            text_edit_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            # set cursor to textedit
            self.textEdit.setTextCursor(text_edit_cursor)
            # get the char of that position
            defcharfmt = self.textEdit.currentCharFormat()
            # deep copy
            newcharfmt = defcharfmt
            # set foreground color of word => the color of word
            newcharfmt.setForeground(Qt.black)
            self.textEdit.setCurrentCharFormat(newcharfmt)
            # clear Focus cursor
            text_edit_cursor.movePosition(QTextCursor.PreviousCharacter)
            self.textEdit.setTextCursor(text_edit_cursor)
            self.textEdit.clearFocus()

    @pyqtSlot()
    def on_text_changed(self):
        # when the length of txt is larger than 300, change the size of txt
        length = len(self.textEdit.toPlainText())
        if length < 400:
            self.textEdit.setStyleSheet(
                'QTextEdit{font-size: 15px; font-family: "raleway_300"; border:none; color: black}')
        elif length >= 400 and length < 800:
            self.textEdit.setStyleSheet(
                'QTextEdit{font-size: 13px; font-family: "raleway_300"; border:none; color: black}')
        else:
            self.textEdit.setStyleSheet(
                'QTextEdit{font-size: 12px; font-family: "raleway_300"; border:none; color: black}')

    def showVolumePanel(self):
        # get global position
        voice_btn_pos = self.setVolume.pos() + self.pos()

        self.sliderWidget.setPosition(voice_btn_pos.x() - 12, voice_btn_pos.y() - 75)

        self.sliderWidget.show()

    def handleVoiceFile(self, type):
        if type == 'upload':
            # get the txt file
            fnames = QFileDialog.getOpenFileName(self, 'Open a text file', './files', '*.txt')
            if fnames[0]:
                self.load_file(fnames[0])
        elif type == 'save':
            # start a thread to start voice saving
            # show the dialog of saving
            if not self.speecher.is_reading_finished():
                return
            self.show_dialog()
            self.voice_saver.set_txt(self.speecher.get_txt())
            self.voice_saver.set_voice_rate(self.speecher.get_rate())
            self.voice_saver.set_voice_type(self.speecher.get_voice_type())
            self.voice_saver.set_voice_name(self.speecher.get_txt())
            voice_save_thread = threading.Thread(target=self.voice_saver.start_save)
            voice_save_thread.start()

    def show_dialog(self):
        # disable btn
        self.save_to_file.setDisabled(True)
        global_pos = self.pos()

        target_pos = {'x': (self.width() - 160) / 2,
                      'y': (self.height() - 120) / 2}

        self.loading_dialog.setPosition(global_pos.x() + target_pos['x'], global_pos.y() + target_pos['y'])
        self.loading_dialog.show()

    def close_dialog(self):
        self.save_to_file.setEnabled(True)
        self.loading_dialog.close()

    def load_file(self, filename):
        name = filename.split('/')[-1]
        self.voice_file_name.setText(name if len(name) < 20 else name[:20] + '...')
        self.textEdit.clear()
        with open(filename, mode='r', encoding='utf-8') as f:
            self.textEdit.setPlainText(f.read())

    def changeVoice(self, type):
        for key in self.type_voices.keys():
            if self.type_voices[key] == type:
                self.speecher.set_voice_type(key)
                return

    def changeVolume(self, volume):
        self.speecher.set_voice_volume(volume)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def closeEvent(self, QCloseEvent):
        reply = QMessageBox.warning(self, 'Warning', 'Do You Want To Exit?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWidget = MainWidget()
    sys.exit(app.exec_())
