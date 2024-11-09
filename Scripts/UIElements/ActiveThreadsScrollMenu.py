from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy, QScrollArea, QWidget, QVBoxLayout, QSpacerItem
from PyQt6.QtGui import QColor, QFont

from .ThreadFrame import ThreadFrame

import random

class ActiveThreadsScrollMenu(QScrollArea):
    def __init__(self, parent=None, max_threads=6):
        super().__init__()

        self._layout_container = QWidget()
        self._layout = QGridLayout()
        self._threads = []
        self._max_threads = max_threads
        self.xPos = 0
        self.yPos = 0

        self._layout_container.setLayout(self._layout)
        self.setWidget(self._layout_container)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        vscrollbar = self.verticalScrollBar()
        vscrollbar.setSingleStep(5)
        self.setWidgetResizable(True)

        for thread in range(self._max_threads):
            self.addThread(thread)
        
        self.addSpacer()
    
    def addThread(self,thread_index):
        modpack_frame = ThreadFrame(thread_index=thread_index)
        modpack_frame.setProgress(0)
        self._layout.addWidget(modpack_frame,self.xPos,self.yPos)
        self._threads.append(modpack_frame)

        self.yPos += 1
        if self.yPos > 1:
            self.yPos = 0
            self.xPos += 1
    
    def addSpacer(self):
        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self._layout.addItem(spacer)