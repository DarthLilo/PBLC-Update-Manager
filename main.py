import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton


class PBLCWindowLaunch(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PBLC Update Manager")

        button = QPushButton("Press Me!")

        self.setFixedSize(QSize(400,300))
        self.setCentralWidget(button)








# ACTUALLY START THE WINDOW

app = QApplication(sys.argv)
window = PBLCWindowLaunch()
window.show()

app.exec()