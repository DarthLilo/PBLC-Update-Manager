from PyQt6.QtCore import QSize, Qt, pyqtProperty
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont

from .ModpackScrollMenu import ModpackScrollMenu

class ModpackSelection(QWidget):
    def __init__(self, modpack_jsons):
        super().__init__()
        self._grid_layout = QVBoxLayout()
        self.setLayout(self._grid_layout)

        self.menu_label = QLabel("Modpack Selection:")
        self.menu_label.setFont(QFont("IBM 3270", 20))
        self._grid_layout.addWidget(self.menu_label)

        self.modpack_frame = ModpackScrollMenu()
        self._grid_layout.addWidget(self.modpack_frame)

        for modpack in modpack_jsons:
            self.modpack_frame.addModpack(modpack_icon="",
                                          modpack_name=modpack['name'],
                                          modpack_author=modpack['author'],
                                          modpack_version=modpack['version'],
                                          mod_count=modpack['mod_count'])