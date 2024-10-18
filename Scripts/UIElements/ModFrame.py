from PyQt6.QtCore import (
    Qt, QSize)

from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy, QHBoxLayout, QSpacerItem, QWidget, QPushButton
from PyQt6.QtGui import QColor, QPalette, QPixmap, QFont, QIcon

from .ClickableLabel import ClickableLabel
from .AnimatedToggle import AnimatedToggle

import os, random

class ModFrame(QFrame):
    def __init__(self, parent=None, mod_icon="", mod_name="Mod",mod_author="Author",mod_version="1.0.0"):
        super().__init__()

        self._layout = QHBoxLayout()
        self.mod_icon = mod_icon
        self.mod_name = mod_name
        self.mod_author = mod_author
        self.mod_version = mod_version
        self.mod_update_version = "0.0.0"
        self.mod_enabled = bool(random.randint(0,3))
        self.updateable = bool(random.randint(0,1))
        self.inSearch = True
        self.inFilter = True
        self.curFilter = "All"

        self.setLayout(self._layout)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)

        self.generateIcons()

        self.draw()

    def generateIcons(self):
        # Drawing icon
        if os.path.exists(self.mod_icon):
            mod_icon_path = self.mod_icon
        else:
            mod_icon_path = "E:\\Lilos Coding\\PBML\\assets\\missing_icon.png"
        
        self._mod_icon_pixmap = QPixmap(mod_icon_path).scaled(QSize(80,80),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation)
    
    def draw(self):
        self.mod_icon_label = QLabel("mod_icon")
        self.mod_icon_label.setPixmap(self._mod_icon_pixmap)
        self.mod_icon_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(self.mod_icon_label)

        # Mod Data

        self.mod_data_container = QWidget()
        self.mod_data_layout = QGridLayout(self.mod_data_container)
        self.mod_data_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.mod_name_label = ClickableLabel(self.LabelClicked,self.HoverEvent,text=self.mod_name,author=self.mod_author,name=self.mod_name,version=self.mod_version)
        self.mod_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mod_name_label.setFont(QFont("IBM 3270", 16))
        self.mod_name_label.setContentsMargins(10,5,0,0)
        self.mod_name_label_defualt = self.mod_name_label.palette()
        self.mod_name_label_hover = self.mod_name_label.palette()
        self.mod_name_label_hover.setColor(self.mod_name_label.foregroundRole(), QColor("#39a7ff"))
        self.mod_data_layout.addWidget(self.mod_name_label)

        if self.updateable:
            self.version_text = f"({self.mod_version}    <    {self.mod_update_version})"
            self.version_color = "#57ff7e"
        else:
            self.version_text = f"({self.mod_version})"
            self.version_color = "#c3c3c3"

        self.mod_version_label = QLabel(self.version_text)
        self.mod_version_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mod_version_label.setFont(QFont("IBM 3270", 10))
        self.mod_version_label.setContentsMargins(6,8,0,0)
        self.mod_version_label_grey = self.mod_version_label.palette()
        self.mod_version_label_grey.setColor(self.mod_version_label.foregroundRole(), QColor(self.version_color))
        self.mod_version_label.setPalette(self.mod_version_label_grey)
        self.mod_data_layout.addWidget(self.mod_version_label,0,1)

        self.mod_author_label = QLabel(self.mod_author)
        self.mod_author_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mod_author_label.setFont(QFont("IBM 3270", 12))
        self.mod_author_label.setContentsMargins(10,5,0,0)
        self.mod_author_label_grey = self.mod_version_label.palette()
        self.mod_author_label_grey.setColor(self.mod_version_label.foregroundRole(), QColor("#c3c3c3"))
        self.mod_author_label.setPalette(self.mod_author_label_grey)
        self.mod_data_layout.addWidget(self.mod_author_label,1,0)

        self._layout.addWidget(self.mod_data_container)

        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._layout.addItem(spacer)

        # Actions

        self.mod_toggle = AnimatedToggle(squish_amount=2.5)
        self.mod_toggle.setChecked(self.mod_enabled)
        self._layout.addWidget(self.mod_toggle,alignment=Qt.AlignmentFlag.AlignRight)
        self.mod_toggle.stateChanged.connect(self.update_state)

        self.refresh_mod = QPushButton()
        self.refresh_mod.setIcon(QIcon("E:\\Lilos Coding\\PBML\\PBLC Update Manager\\assets\\refresh.png"))
        self.refresh_mod.setIconSize(QSize(30,30))
        self._layout.addWidget(self.refresh_mod,alignment=Qt.AlignmentFlag.AlignRight)
        

        self.delete_mod = QPushButton()
        self.delete_mod.setIcon(QIcon("E:\\Lilos Coding\\PBML\\PBLC Update Manager\\assets\\trash_can.png"))
        self.delete_mod.setIconSize(QSize(30,30))
        self._layout.addWidget(self.delete_mod,alignment=Qt.AlignmentFlag.AlignRight)
    
    def update_state(self, event):
        self.mod_enabled = bool(event)
        if self.curFilter == "Disabled":
            self.inFilter = not bool(event)
            self.determine_visibility()
    
    def show(self):
        self.inSearch = True
        self.determine_visibility()

    def hide(self):
        self.inSearch = False
        self.determine_visibility()
    
    def update_filter(self, filter):
        self.curFilter = filter
        if filter == "Updatable" and self.updateable:
            self.inFilter = True
        elif filter == "Disabled" and not self.mod_enabled:
            self.inFilter = True
        else:
            self.inFilter = False
        
        self.determine_visibility()
    
    def determine_visibility(self):
        if self.inFilter and self.inSearch:
            self.setVisible(True)
        else:
            self.setVisible(False)
    
    def LabelClicked(self, event, data):
        button = event.button()
        modifiers = event.modifiers()

        if modifiers == Qt.KeyboardModifier.NoModifier and button == Qt.MouseButton.LeftButton:
            print(data)
        return
    
    def HoverEvent(self, hover):
        if hover:
            self.mod_name_label.setPalette(self.mod_name_label_hover)
        else:
            self.mod_name_label.setPalette(self.mod_name_label_defualt)