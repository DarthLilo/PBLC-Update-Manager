from PyQt6.QtCore import QSize, Qt, pyqtProperty
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QStackedWidget
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont

from . import UIElements
from . import Modpacks

import time

class UI(QWidget):
    def __init__(self, assets_folder):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._assets_folder=assets_folder
        self.LoadFonts()

        self.screen_container = QStackedWidget()
        self._layout.addWidget(self.screen_container)


        # Screens
        self._screen_loading = None
        self._screen_modpack_selection = None

        #Starting
        self.ShowLoadingScreen()
        
    
    def LoadFonts(self):
        lethal_font = QFontDatabase.addApplicationFont(f"{self._assets_folder}/3270-Regular.ttf")
        #families = QFontDatabase.applicationFontFamilies(lethal_font)
    
    def ShowLoadingScreen(self, prev_menu = None):
        if not self._screen_loading:
            self._screen_loading = UIElements.LoadingScreen()

        if prev_menu:
            self.screen_container.removeWidget(prev_menu)
            print(f"removed {prev_menu}")
    
        self.screen_container.addWidget(self._screen_loading)
        return
    
    def FadeToModpackSelection(self, prev_menu):
        if not self._screen_modpack_selection:
            self._screen_modpack_selection = UIElements.ModpackSelection(Modpacks.List())

        fader = UIElements.FaderWidget(prev_menu,self._screen_modpack_selection)
        self.screen_container.removeWidget(prev_menu)
        self.screen_container.addWidget(self._screen_modpack_selection)