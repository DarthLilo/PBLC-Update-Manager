from PyQt6.QtCore import (
    Qt, QSize)

from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy
from PyQt6.QtGui import QColor, QPalette, QPixmap, QFont
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect

from .ClickableLabel import ClickableLabel
from ..Assets import Assets
from ..Launch import Launch
from ..Modpacks import Modpacks

import os, winaccent
from PIL import Image
from PIL.ImageQt import ImageQt

class ModpackFrame(QFrame):
    def __init__(self, parent=None, modpack_icon="", modpack_name="Modpack",modpack_author="Author",modpack_version="1.0.0",mod_count=0,xyCords=(0,0),screen_func=None):
        super().__init__()
        
        self.grid_layout = QGridLayout()

        self.modpack_icon = modpack_icon
        self.modpack_name = modpack_name
        self.modpack_author = modpack_author
        self.modpack_version = modpack_version
        self.mod_count = mod_count
        self._xyCords = xyCords
        self._screen_func = screen_func
        self.setObjectName("ModpackFrameWidget")

        if winaccent.system_uses_light_theme:
            self.darker_text_color = "#242424"
            self.setStyleSheet(
            """
            QWidget#ModpackFrameWidget {
                background-color:#d1d1d1;
                border-radius: 10px;
            }
            QFrame#ModpackFrameWidget::hover{
                background-color:#e3e3e3;
                border-radius: 10px;
            }
            """
            )
        else:
            self.darker_text_color = "#c3c3c3"
            self.setStyleSheet(
            """
            QWidget#ModpackFrameWidget {
                background-color:#323232;
                border-radius: 10px;
            }
            QFrame#ModpackFrameWidget::hover{
                background-color:#474747;
                border-radius: 10px;
            }
            """
            )

        

        self.generateIcons()
        self.setLayout(self.grid_layout)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        
        self.draw()
        
    def generateIcons(self):
        # Drawing icon
        if os.path.exists(self.modpack_icon):
            modpack_icon_path = self.modpack_icon
        else:
            modpack_icon_path = Assets.getResource(Assets.ResourceTypes.missing)
        
        gradient_overlay = Assets.getResource(Assets.ResourceTypes.gradient_overlay)

        modpack_icon_pil = Image.open(modpack_icon_path)
        modpack_icon_pil = modpack_icon_pil.resize((256,256))

        self._ModpackIconNormal = QPixmap(modpack_icon_path)
        self._ModpackIconNormal = self._ModpackIconNormal.scaled(QSize(150,150),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation)
        self.modpack_pixmap = self._ModpackIconNormal
    
    def draw(self):

        self.modpack_label = ClickableLabel(self.label_clicked,text="modpack_icon",xyCords=self._xyCords,
                                            author=self.modpack_author,name=self.modpack_name,
                                            version=self.modpack_version,icon_path=self.modpack_icon,
                                            mod_count=self.mod_count,
                                            modpack_context_menu=True, edit_screen_func=self._screen_func)
        self.modpack_label.setPixmap(self.modpack_pixmap)
        self.modpack_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.modpack_label)

        # Drawing Modpack Name
        modpack_name_label = ClickableLabel(self.label_clicked,text=self.modpack_name,xyCords=self._xyCords,
                                            author=self.modpack_author,name=self.modpack_name,
                                            version=self.modpack_version,icon_path=self.modpack_icon,
                                            mod_count=self.mod_count,
                                            modpack_context_menu=True, edit_screen_func=self._screen_func)
                                            
        modpack_name_label.setFont(QFont("IBM 3270", 16))
        modpack_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(modpack_name_label)

        if winaccent.system_uses_light_theme:
            modpack_name_label.setStyleSheet(
            """
            ClickableLabel {
                color:#000000;
            }
            ClickableLabel::hover{
                color:#4571ff;
            }
            """
            )
        else:
            modpack_name_label.setStyleSheet(
            """
            ClickableLabel {
                color:#ffffff;
            }
            ClickableLabel::hover{
                color:#4298fb;
            }
            """
            )

        #Drawing Modpack Author Version
        modpack_author_version_label = QLabel(f"{self.modpack_author} - {self.modpack_version}")
        modpack_author_version_label.setFont(QFont("IBM 3270", 12))

        p = modpack_author_version_label.palette()
        p.setColor(modpack_author_version_label.foregroundRole(), QColor(self.darker_text_color))
        modpack_author_version_label.setPalette(p)

        modpack_author_version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(modpack_author_version_label)

        #Drawing Modpack Mod Count
        self.modpack_mod_count_label = QLabel(f"({self.mod_count} Mods)")
        self.modpack_mod_count_label.setFont(QFont("IBM 3270", 12))

        p = self.modpack_mod_count_label.palette()
        p.setColor(self.modpack_mod_count_label.foregroundRole(), QColor(self.darker_text_color))
        self.modpack_mod_count_label.setPalette(p)

        self.modpack_mod_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.modpack_mod_count_label)

        return
    
    def label_clicked(self, event, data):
        button = event.button()
        modifiers = event.modifiers()
        if modifiers == Qt.KeyboardModifier.NoModifier and button == Qt.MouseButton.LeftButton:
            Launch.Start(data['author'],data['name'])
            #self._screen_func(data)
        return

    def UpdateFrameModCount(self,value):
        try:
            self.modpack_mod_count_label.setText(f"({value} Mods)")
        except RuntimeError:
            pass