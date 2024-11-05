from PyQt6.QtCore import (
    Qt, QSize)

from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy, QHBoxLayout, QSpacerItem, QWidget, QPushButton, QVBoxLayout, QProgressBar
from PyQt6.QtGui import QColor, QPalette, QPixmap, QFont, QIcon

from ..Assets import Assets

import os, random

class ThreadFrame(QFrame):
    def __init__(self, parent=None, thread_index=0):
        super().__init__()

        self._layout = QHBoxLayout(self)
        self._thread_index = thread_index

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)

        self.draw()

    def draw(self):

        self.thread_icon_label = QLabel("thread_icon_label")
        self.thread_icon_label.setPixmap(QPixmap(Assets.getResource(Assets.ResourceTypes.inactive_thread)).scaled(QSize(105,105),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation))
        self._layout.addWidget(self.thread_icon_label)

        self.thread_info_container = QFrame()
        self.thread_info_layout = QVBoxLayout(self.thread_info_container)
        self.thread_info_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)


        self.thread_name_label = QLabel(f"Inactive Thread {self._thread_index}")
        self.thread_name_label.setFont(QFont("IBM 3270", 12))
        self.thread_info_layout.addWidget(self.thread_name_label)

        self.thread_progress_bar = QProgressBar()
        self.thread_progress_bar.setValue(0)
        self.thread_progress_bar.setFont(QFont("IBM 3270", 10))
        self.thread_info_layout.addWidget(self.thread_progress_bar)
        
        self._layout.addWidget(self.thread_info_container)
    
    def setIcon(self,qpixmap:QPixmap):
        self.thread_icon_label.setPixmap(qpixmap.scaled(QSize(105,105),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation))
    
    def setName(self, name):
        self.thread_name_label.setText(str(name))
    
    def setProgress(self,progress):
        """Whole value ints for progress, 50% would be 50"""
        self.thread_progress_bar.setValue(int(progress))