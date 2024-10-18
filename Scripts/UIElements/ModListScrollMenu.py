from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy, QScrollArea, QWidget, QVBoxLayout, QSpacerItem
from PyQt6.QtGui import QColor, QFont

from .ModFrame import ModFrame

class ModListSrollMenu(QScrollArea):
    def __init__(self, parent=None):
        super().__init__()

        self._layout_container = QWidget()
        self._layout = QVBoxLayout()
        self.mods = []
        self.mod_names = []

        self._layout_container.setLayout(self._layout)
        self.setWidget(self._layout_container)
        

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        vscrollbar = self.verticalScrollBar()
        vscrollbar.setSingleStep(5)
        self.setWidgetResizable(True)

        

        return
    
    def addMod(self, mod_icon = "",mod_name = "ModNameReal", mod_author="Author",mod_version="1.0.0"):
        modpack_frame = ModFrame(mod_icon=mod_icon,mod_name=mod_name,mod_author=mod_author,mod_version=mod_version)
        self._layout.addWidget(modpack_frame)
        self.mods.append(modpack_frame)
        self.mod_names.append(mod_name)
    
    def addSpacer(self):
        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self._layout.addItem(spacer)
    

    def getMods(self):
        return self.mods
    
    def getModNames(self):
        return self.mod_names