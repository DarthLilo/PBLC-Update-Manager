from PyQt6.QtCore import QSize, Qt, pyqtProperty
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont

from .ModpackScrollMenu import ModpackScrollMenu

class PBLCMainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self._grid_layout = QVBoxLayout()
        self.setLayout(self._grid_layout)

        self.menu_label = QLabel("Modpack Selection:")
        self.menu_label.setFont(QFont("IBM 3270", 20))
        self._grid_layout.addWidget(self.menu_label)

        self.modpack_frame = ModpackScrollMenu()
        self._grid_layout.addWidget(self.modpack_frame)
        
        #for name in modpack_names:
        #    self.modpack_frame.addModpack(modpack_name=name)