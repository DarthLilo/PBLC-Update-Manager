from PyQt6.QtCore import QSize, Qt, pyqtProperty, QRect
from PyQt6.QtWidgets import QPushButton, QComboBox
from PyQt6.QtGui import QCursor

class HoverButton(QPushButton):
    def __init__(self, text = "", **kwargs):
        QPushButton.__init__(self, text, **kwargs)

        self.default_cursor = self.cursor()
        self.hover_cursor = QCursor(Qt.CursorShape.PointingHandCursor)
    
    def enterEvent(self, event):
        self.setCursor(self.hover_cursor)
    
    def leaveEvent(self, a0):
        self.setCursor(self.default_cursor)

class HoverComboBox(QComboBox):
    def __init__(self, **kwargs):
        QComboBox.__init__(self, **kwargs)

        self.default_cursor = self.cursor()
        self.hover_cursor = QCursor(Qt.CursorShape.PointingHandCursor)
    
    def enterEvent(self, event):
        self.setCursor(self.hover_cursor)
    
    def leaveEvent(self, a0):
        self.setCursor(self.default_cursor)