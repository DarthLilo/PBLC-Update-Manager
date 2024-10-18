from PyQt6.QtCore import (
    Qt, QSize)

from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy
from PyQt6.QtGui import QColor, QPalette, QPixmap, QFont

from .ClickableLabel import ClickableLabel

import os
from PIL import Image
from PIL.ImageQt import ImageQt

class ModpackFrame(QFrame):
    def __init__(self, parent=None, modpack_icon="", modpack_name="Modpack",modpack_author="Author",modpack_version="1.0.0",mod_count=0,xyCords=(0,0)):
        super().__init__()
        
        self.grid_layout = QGridLayout()

        self.modpack_icon = modpack_icon
        self.modpack_name = modpack_name
        self.modpack_author = modpack_author
        self.modpack_version = modpack_version
        self.mod_count = mod_count
        self._xyCords = xyCords

        self.generateIcons()
        self.setLayout(self.grid_layout)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        #self.setColor(QColor("black"))
        self.draw()
        
    def generateIcons(self):
        # Drawing icon
        if os.path.exists(self.modpack_icon):
            modpack_icon_path = "E:\\Lilos Coding\\PBML\\assets\\missing_icon.png"
        else:
            modpack_icon_path = "E:\\Lilos Coding\\PBML\\assets\\missing_icon.png"
        
        gradient_overlay = "E:\\Lilos Coding\\PBML\\assets\\gradient_overlay.png"

        modpack_icon_pil = Image.open(modpack_icon_path)
        gradient_overlay_pil = Image.open(gradient_overlay)
        modpack_icon_pil.paste(gradient_overlay_pil, (0,0), mask = gradient_overlay_pil)

        self._ModpackIconNormal = QPixmap(modpack_icon_path)
        self._ModpackIconHover = QPixmap.fromImage(ImageQt(modpack_icon_pil))
        self._ModpackIconNormal = self._ModpackIconNormal.scaled(QSize(150,150),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation)
        self._ModpackIconHover = self._ModpackIconHover.scaled(QSize(150,150),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation)
        self.modpack_pixmap = self._ModpackIconNormal
    
    def draw(self):

        self.modpack_label = ClickableLabel(self.label_clicked,text="modpack_icon",xyCords=self._xyCords,hoverEvent=self.label_hover)
        self.modpack_label.setPixmap(self.modpack_pixmap)
        self.modpack_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.modpack_label)

        # Drawing Modpack Name
        modpack_name_label = QLabel(self.modpack_name)
        modpack_name_label.setFont(QFont("IBM 3270", 16))
        modpack_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(modpack_name_label)

        #Drawing Modpack Author Version
        modpack_author_version_label = QLabel(f"{self.modpack_author} - {self.modpack_version}")
        modpack_author_version_label.setFont(QFont("IBM 3270", 12))

        p = modpack_author_version_label.palette()
        p.setColor(modpack_author_version_label.foregroundRole(), QColor("#c3c3c3"))
        modpack_author_version_label.setPalette(p)

        modpack_author_version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(modpack_author_version_label)

        #Drawing Modpack Mod Count
        modpack_mod_count_label = QLabel(f"({self.mod_count} Mods)")
        modpack_mod_count_label.setFont(QFont("IBM 3270", 12))

        p = modpack_mod_count_label.palette()
        p.setColor(modpack_mod_count_label.foregroundRole(), QColor("#c3c3c3"))
        modpack_mod_count_label.setPalette(p)

        modpack_mod_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(modpack_mod_count_label)

        return
    
    def label_clicked(self, event, data):
        button = event.button()
        modifiers = event.modifiers()

        if modifiers == Qt.KeyboardModifier.NoModifier and button == Qt.MouseButton.LeftButton:
            print(f'omg [{data[['author']],"",data['name']}] was clicked')
        return

    def label_hover(self, hover):
        if hover:
            self.modpack_pixmap = self._ModpackIconHover
        else:
            self.modpack_pixmap = self._ModpackIconNormal
        
        self.modpack_label.setPixmap(self.modpack_pixmap)

        return
    
    def show(self):
        self.setVisible(True)
    
    def hide(self):
        self.setVisible(False)