from PyQt6.QtCore import QSize, Qt, pyqtProperty
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QMenu, QToolBar, QStatusBar, QDialog
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase

from . import UIElements
from .Logging import Logging
import os

class UI():
    """The main PBLC UI class"""

    assets_folder = ""

    def __init__(self,assets_folder):
        Logging.New("Loading UI Systems...")

        UI.assets_folder = assets_folder
        
        return

    def LoadFonts():
        lethal_font = QFontDatabase.addApplicationFont(f"{UI.assets_folder}/3270-Regular.ttf")
        families = QFontDatabase.applicationFontFamilies(lethal_font)
        Logging.New(f"Loaded {families[0]}")

    def ModpackSelectionScreen():
        return