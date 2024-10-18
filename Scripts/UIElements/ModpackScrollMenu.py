from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy, QScrollArea, QWidget
from PyQt6.QtGui import QColor, QFont

from .ModpackFrame import ModpackFrame

class ModpackScrollMenu(QScrollArea):
    def __init__(self, parent=None):
        super().__init__()

        self._layout_container = QWidget()
        self._grid_layout = QGridLayout()
        self._xPos = 0
        self._yPos = 0
        self.modpacks = []

        self._layout_container.setLayout(self._grid_layout)
        self.setWidget(self._layout_container)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        vscrollbar = self.verticalScrollBar()
        vscrollbar.setSingleStep(5)
        self.setWidgetResizable(True)

        return
    
    def addModpack(self, modpack_icon = "",modpack_name = "Modpack", modpack_author="Author",modpack_version="1.0.0",mod_count=0):
        modpack_frame = ModpackFrame(modpack_icon=modpack_icon,modpack_name=modpack_name,modpack_author=modpack_author,modpack_version=modpack_version,mod_count=mod_count,xyCords=(self._xPos,self._yPos))
        modpack_frame.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self._grid_layout.addWidget(modpack_frame,self._xPos,self._yPos)
        self.modpacks.append(modpack_frame)
        self._yPos += 1
        if self._yPos >= 5:
            self._yPos = 0
            self._xPos += 1
    
    def getModpacks(self):
        return self.modpacks
    