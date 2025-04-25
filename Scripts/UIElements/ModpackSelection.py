from PyQt6.QtCore import QSize, Qt, pyqtProperty
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QPushButton, QComboBox
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont, QColor

from .ModpackScrollMenu import ModpackScrollMenu
from ..Assets import Assets

class ModpackSelection(QWidget):
    def __init__(self, modpack_jsons,edit_modpack_func, add_modpack_func,back_to_game_selection):
        super().__init__()
        self._grid_layout = QGridLayout()
        self.setLayout(self._grid_layout)
        self.add_modpack_func = add_modpack_func
        self.edit_modpack_func = edit_modpack_func

        self.menu_label = QLabel("Modpack Selection:")
        self.menu_label.setFont(QFont("IBM 3270", 20))
        self._grid_layout.addWidget(self.menu_label,0,0)

        self.info_label = QLabel("(Click a modpack to launch it, or right-click for more options!)")
        self.info_label.setFont(QFont("IBM 3270", 14))
        self._grid_layout.addWidget(self.info_label,1,0)

        p = self.info_label.palette()
        p.setColor(self.info_label.foregroundRole(), QColor("#707070"))
        self.info_label.setPalette(p)

        self.import_modpack = QPushButton("Import Modpack")
        self.import_modpack.setIcon(QIcon(Assets.getResource(Assets.IconTypes.download,True)))
        self.import_modpack.clicked.connect(lambda: self.addModpackScreen(type=0))
        self._grid_layout.addWidget(self.import_modpack,0,10)

        self.add_modpack = QPushButton("New Modpack")
        self.add_modpack.setIcon(QIcon(Assets.getResource(Assets.IconTypes.plus,True)))
        self.add_modpack.clicked.connect(lambda: self.addModpackScreen(type=1))
        self._grid_layout.addWidget(self.add_modpack,0,11)

        self.modpack_frame = ModpackScrollMenu()
        self._grid_layout.addWidget(self.modpack_frame,2,0,1,12)

        self.back_to_games = QPushButton("Back to Game Selection")
        self.back_to_games.setIcon(QIcon(Assets.getResource(Assets.IconTypes.back_arrow,True)))
        self.back_to_games.clicked.connect(back_to_game_selection)
        self._grid_layout.addWidget(self.back_to_games,3,0,1,1)
        self.back_to_games.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

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
    
    def addModpackScreen(self, type=0):
        self.add_modpack_func(type=type)