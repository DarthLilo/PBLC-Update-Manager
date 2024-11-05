from PyQt6.QtCore import QSize, Qt, pyqtProperty
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QPushButton, QComboBox
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont

from .ModpackScrollMenu import ModpackScrollMenu
from ..Assets import Assets

class ModpackSelection(QWidget):
    def __init__(self, modpack_jsons,edit_modpack_func, add_modpack_func):
        super().__init__()
        self._grid_layout = QGridLayout()
        self.setLayout(self._grid_layout)
        self.add_modpack_func = add_modpack_func
        self.edit_modpack_func = edit_modpack_func

        self.menu_label = QLabel("Modpack Selection:")
        self.menu_label.setFont(QFont("IBM 3270", 20))
        self._grid_layout.addWidget(self.menu_label,0,0)

        self.new_modpack_type = QComboBox()
        self.new_modpack_type.addItems(["Import","Fresh"])
        self._grid_layout.addWidget(self.new_modpack_type,0,9)

        self.add_modpack = QPushButton("")
        self.add_modpack.setIcon(QIcon(Assets.getResource(Assets.IconTypes.plus)))
        self.add_modpack.clicked.connect(self.addModpackScreen)
        self._grid_layout.addWidget(self.add_modpack,0,10)

        self.modpack_frame = ModpackScrollMenu()
        self._grid_layout.addWidget(self.modpack_frame,1,0,1,11)

        for modpack in modpack_jsons:
            self.modpack_frame.addModpack(modpack_icon=modpack['icon'],
                                          modpack_name=modpack['name'],
                                          modpack_author=modpack['author'],
                                          modpack_version=modpack['version'],
                                          mod_count=modpack['mod_count'],
                                          screen_func=edit_modpack_func)
    def rescanModpacks(self, modpack_jsons):
        self.modpack_frame.clearModpacks()
        for modpack in modpack_jsons:
            self.modpack_frame.addModpack(modpack_icon=modpack['icon'],
                                          modpack_name=modpack['name'],
                                          modpack_author=modpack['author'],
                                          modpack_version=modpack['version'],
                                          mod_count=modpack['mod_count'],
                                          screen_func=self.edit_modpack_func)
    
    def addModpackScreen(self, s):
        self.add_modpack_func(type=self.new_modpack_type.currentIndex())