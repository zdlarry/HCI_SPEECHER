import time
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class VoiceTimer(QObject):
    """
     To start a timer for the voice reading
    """
    timer_min_up = pyqtSignal()
    timer_hour_up = pyqtSignal()
    timer_update = pyqtSignal(str)

    def __init__(self):
        super(VoiceTimer, self).__init__()
        self.set_initial_time()
        self.set_reading_timer()
        self.build_connections()

    def set_initial_time(self):
        self.timer_label = '00:00:00'
        self.timer_hour = 0
        self.timer_min = 0
        self.timer_second = 0

    def get_initial_time(self):
        return self.timer_label

    def set_reading_timer(self):
        self.reading_timer = QTimer(self)
        self.reading_timer.timeout.connect(self.change_time_sec)

    def build_connections(self):
        self.timer_min_up.connect(self.set_timer_min_up)
        self.timer_hour_up.connect(self.set_timer_hour_up)

    def change_time_sec(self):
        if self.timer_second >= 59:
            # if second == 59, set second = 0 and set min += 1
            self.timer_min_up.emit()
            self.timer_second = 0
        else:
            self.timer_second += 1
            self.timer_update.emit(self.set_timer_label())
            # print(self.set_timer_label())

    def set_timer_label(self):
        hour_str = '0' + str(self.timer_hour) if self.timer_hour < 10 else str(self.timer_hour)
        min_str = '0' + str(self.timer_min) if self.timer_min < 10 else str(self.timer_min)
        second_str = '0' + str(self.timer_second) if self.timer_second < 10 else str(self.timer_second)

        return hour_str + ':' + min_str + ':' + second_str

    def start_timer(self):
        '''
        Func to start a new timer
        '''
        self.set_initial_time()
        self.reading_timer.start(1000)

    def stop_timer(self):
        '''
        Func to stop a timer
        '''
        self.set_initial_time()
        self.reading_timer.stop()

    @pyqtSlot()
    def set_timer_min_up(self):
        if self.timer_min >= 59:
            self.timer_hour_up.emit()
            self.timer_min = 0
            return

        self.timer_min += 1
        self.timer_update.emit(self.set_timer_label())
        # print(self.set_timer_label())

    @pyqtSlot()
    def set_timer_hour_up(self):
        self.timer_hour += 1
        self.timer_update.emit(self.set_timer_label())
        # print(self.set_timer_label())


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     t = QThread()
#     voiceTimer = VoiceTimer()
#     voiceTimer.moveToThread(t)
#     t.started.connect(voiceTimer.start_timer)
#     t.start()
#     sys.exit(app.exec_())
