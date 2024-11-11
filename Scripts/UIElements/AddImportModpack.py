from PyQt6.QtCore import QSize, Qt, pyqtProperty, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QFrame, QSpacerItem, QHBoxLayout, QCompleter, QComboBox, QPushButton, QTabBar, QFileDialog, QToolTip, QScrollArea, QDialog
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont, QPixmap, QColor

from ..Assets import Assets
from ..Logging import Logging
from ..Modpacks import Modpacks
from ..Networking import Networking
from packaging import version

import os

class AddImportModpack(QDialog):
    def __init__(self,parent=None, type=0, show_download_screen_func = None, update_cache_screen_func = None, cache_status_func = None, clear_modpack = None, refresh_modpacks = None):
        super().__init__()

        # type 0 =  import, type 1 is manual
        self._type = type
        self._show_download_screen_func = show_download_screen_func
        self._update_cache_screen_func = update_cache_screen_func
        self._cache_status_func = cache_status_func
        self._clear_modpack = clear_modpack
        self._refresh_modpacks = refresh_modpacks

        self._layout = QGridLayout(self)
        self.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))
        self.setWindowTitle("Create/Import Modpack")

        if type == 0:
            self.modpack_source = QLineEdit()
            self.modpack_source.setPlaceholderText("Filepath or URL to source")
            self._layout.addWidget(self.modpack_source,0,0)

            self.modpack_source_button = QPushButton()
            self.modpack_source_button.setIcon(QIcon(Assets.getResource(Assets.IconTypes.folder,True)))
            self.modpack_source_button.clicked.connect(self.OpenFilepathDialog)
            self._layout.addWidget(self.modpack_source_button,0,1)


        if type == 1:
            self.modpack_name = QLineEdit()
            self.modpack_name.setPlaceholderText("Modpack Name...")
            self._layout.addWidget(self.modpack_name,0,0,1,2)

            self.modpack_author = QLineEdit()
            self.modpack_author.setPlaceholderText("Modpack Author...")
            self._layout.addWidget(self.modpack_author,1,0)

            self.modpack_version = QLineEdit()
            self.modpack_version.setPlaceholderText("1.0.0")
            self._layout.addWidget(self.modpack_version,1,1)

            self.modpack_icon = QLineEdit()
            self.modpack_icon.setPlaceholderText("Modpack Icon Path...")
            self._layout.addWidget(self.modpack_icon,2,0)

            self.modpack_icon_button = QPushButton()
            self.modpack_icon_button.setIcon(QIcon(Assets.getResource(Assets.IconTypes.folder,True)))
            self.modpack_icon_button.clicked.connect(self.OpenFilepathDialog)
            self._layout.addWidget(self.modpack_icon_button)

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.CreateModpackFunc)
        self._layout.addWidget(self.create_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.Cancel)
        self._layout.addWidget(self.cancel_button)
    
    def OpenFilepathDialog(self):
        if self._type == 0:
            file_filter = "Json Files (*.json)"
        elif self._type == 1:
            file_filter = "Image Files (*.png)"

        file_name, _ = QFileDialog.getOpenFileName(self,"Open File","",file_filter)
        if file_name:
            if self._type == 0:
                self.modpack_source.setText(file_name)
            elif self._type == 1:
                self.modpack_icon.setText(file_name)
        return

    def Cancel(self):
        self.close()
    
    def CreateModpackFunc(self):
        if self._type == 0:
            if not Networking.IsURL(self.modpack_source.text()) and not os.path.exists(self.modpack_source.text()):
                Logging.New("Please select a valid modpack path first!")
                return
            self.close()
            Modpacks.ImportVerify(self.modpack_source.text(),self._show_download_screen_func,self._update_cache_screen_func,self._cache_status_func)
            self._clear_modpack()

        elif self._type == 1:

            actual_vers = self.modpack_version.text()
            if not actual_vers:
                actual_vers = "1.0.0"
            
            try:
                version.Version(actual_vers)
            except version.InvalidVersion:
                actual_vers = "1.0.0"

            if not self.modpack_author.text() or not self.modpack_name.text():
                Logging.New("Please fill out all required fields!")
            else:
                Modpacks.New(self.modpack_author.text(),self.modpack_name.text(),actual_vers,icon=self.modpack_icon.text())
                self.close()
                if callable(self._refresh_modpacks): self._refresh_modpacks()