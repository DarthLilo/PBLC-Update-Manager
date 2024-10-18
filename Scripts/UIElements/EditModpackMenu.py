from PyQt6.QtCore import QSize, Qt, pyqtProperty, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QFrame, QSpacerItem, QHBoxLayout, QCompleter, QComboBox, QPushButton
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont, QPixmap, QColor

from .ModListScrollMenu import ModListSrollMenu
from .ModpackInfoFrame import ModpackInfoFrame

import os

class EditModpackMenu(QWidget):
    def __init__(self,modpack_icon="", modpack_name="Modpack",modpack_author="Author",modpack_version="1.0.0",mod_count=0):
        super().__init__()
        self._layout = QGridLayout()
        self.setLayout(self._layout)
        self.modpack_icon = modpack_icon
        self.generateIcons()

        
        self.modpack_info_frame = ModpackInfoFrame(modpack_name,modpack_author,modpack_version,mod_count,self.modpack_icon_pixmap)

        self.mod_list_frame = ModListSrollMenu()
        mods_list = ["more items", "silly mod", "snail cat", "woah","scrap expansion","more emotes", "better emotes", "too many emotes","general improvements","another mod","silly modss again","diversity","moon pack 1", "bozoros","sea slugs", "poo worms", "shit worms", "ice cube reference","munano"]
        for mod in mods_list:
            self.mod_list_frame.addMod(mod_name=mod)
        self.mod_list_frame.addSpacer()


        self.mod_search_frame_layout = QHBoxLayout()
        self.mod_search_frame = QFrame()
        self.mod_search_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.mod_search_frame.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)

        self.search_filters = QComboBox()
        self.search_bar = QLineEdit()
        self.add_mod = QPushButton()
        self.export_modpack = QPushButton()
        self.check_for_updates = QPushButton()
        self.search_bar.setPlaceholderText("Search Mods...")
        self.search_bar.textChanged.connect(self.updateModList)
        self.search_bar.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.mod_search_frame_layout.addWidget(self.search_filters)
        self.mod_search_frame_layout.addWidget(self.search_bar)
        self.mod_search_frame_layout.addWidget(self.export_modpack)
        self.mod_search_frame_layout.addWidget(self.check_for_updates)
        self.mod_search_frame_layout.addWidget(self.add_mod)
        self.mod_search_frame.setLayout(self.mod_search_frame_layout)

        self.search_filters.addItems(["All","Updatable","Disabled"])
        self.search_filters.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Expanding)
        self.search_filters.currentTextChanged.connect(self.updateModFilters)

        self.search_completer = QCompleter(self.mod_list_frame.getModNames())
        self.search_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_bar.setCompleter(self.search_completer)

        self.add_mod.setIcon(QIcon("E:\\Lilos Coding\\PBML\\assets\\plus.png"))
        self.add_mod.setIconSize(QSize(40,40))

        self.export_modpack.setIcon(QIcon("E:\\Lilos Coding\\PBML\\assets\\archive.png"))
        self.export_modpack.setIconSize(QSize(40,40))

        self.check_for_updates.setIcon(QIcon("E:\\Lilos Coding\\PBML\\assets\\download.png"))
        self.check_for_updates.setIconSize(QSize(40,40))


        #mod_search_frame.setStyleSheet("""
        #QFrame {
        #    background: #002025;
        #    border-radius: 40px;
        #    opacity: 100;
        #    border: 2px solid #ff2025;
        #}
        #""")


        self._layout.addWidget(self.modpack_info_frame,0, 0, 7, 1)
        self._layout.addWidget(self.mod_list_frame,1,1,6,3)
        self._layout.addWidget(self.mod_search_frame,0,1,1,3)
    
    def generateIcons(self):
        if os.path.exists(self.modpack_icon):
            modpack_icon_path = self.modpack_icon
        else:
            modpack_icon_path = "E:\\Lilos Coding\\PBML\\assets\\missing_icon.png"
        
        self.modpack_icon_pixmap = QPixmap(modpack_icon_path).scaled(QSize(200,200),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation)
    
    def updateModList(self, text):
        
        for mod in self.mod_list_frame.getMods():
            if text.lower() in mod.mod_name.lower():
                mod.show()
            else:
                mod.hide()
    
    def updateModFilters(self, event):
        if str(event) != "All":
            for mod in self.mod_list_frame.getMods():
                mod.update_filter(str(event))
            
        else:
            for mod in self.mod_list_frame.getMods():
                mod.inFilter = True
                mod.curFilter = "All"
                mod.determine_visibility()