from PyQt6.QtCore import QSize, Qt, pyqtProperty, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QFrame, QSpacerItem, QHBoxLayout, QCompleter, QComboBox, QPushButton, QProgressBar
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont, QPixmap, QColor

from .ActiveThreadsScrollMenu import ActiveThreadsScrollMenu

import threading, datetime, time

class ModpackDownloadScreen(QWidget):
    def __init__(self):
        super().__init__()

        self._layout = QGridLayout(self)
        self.start_time = None
        self._kill_clock = False

        self.mod_download_threads_frame = ActiveThreadsScrollMenu()
        #self.mod_download_threads_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        #self.mod_download_threads_frame.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        
        self.modpack_progress_frame = QFrame()
        self.modpack_progress_layout = QVBoxLayout(self.modpack_progress_frame)
        self.modpack_progress_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        
        self.current_status_label = QLabel("Initializing Download")
        self.current_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_status_label.setFont(QFont("IBM 3270", 16))
        self.modpack_progress_layout.addWidget(self.current_status_label)

        self.current_progress_bar = QProgressBar()
        self.current_progress_bar.setValue(0)
        self.current_progress_bar.setFont(QFont("IBM 3270", 16))
        self.modpack_progress_layout.addWidget(self.current_progress_bar)

        self.elapsed_time = QLabel("00:00:00")
        self.elapsed_time.setFont(QFont("IBM 3270", 16))
        self.elapsed_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.modpack_progress_layout.addWidget(self.elapsed_time)


        
        self._layout.addWidget(self.mod_download_threads_frame,0,0,4,1)
        self._layout.addWidget(self.modpack_progress_frame,5,0,1,1)
    
    def setStatus(self, status):
        self.current_status_label.setText(status)

    def initClock(self):
        self.start_time = datetime.datetime.timestamp(datetime.datetime.now())
        threading.Thread(target=lambda start_time=self.start_time:self.updateClock(start_time),daemon=True).start()
    
    def updateClock(self, start_time):
        if self._kill_clock:
            self._kill_clock
            return
        
        timestamp_start = datetime.datetime.fromtimestamp(start_time)
        timestamp_now = datetime.datetime.now()

        difference = round((timestamp_now-timestamp_start).total_seconds())
        hours, remainder = divmod(difference, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
        self.elapsed_time.setText(formatted_time)

        time.sleep(1)
        self.updateClock(start_time)
    
    def killClock(self):
        self._kill_clock = True