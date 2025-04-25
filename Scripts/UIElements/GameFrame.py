from PyQt6.QtCore import (
    Qt, QSize)

from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QColor, QPalette, QPixmap, QFont

from .ClickableLabel import ClickableLabel, ClickableLabelGame
from ..Assets import Assets
from ..Launch import Launch
from ..Modpacks import Modpacks
from ..Game import Game
from ..Cache import Cache

import os, winaccent
from PIL import Image
from PIL.ImageQt import ImageQt

class GameFrame(QFrame):
    def __init__(self, parent=None, game_icon="", game_name="Game", game_developer="Developer",game_id="game_id",xyCords=(0,1),trigger_menu_func=None):
        super().__init__()

        self.grid_layout = QGridLayout()

        self.game_icon = game_icon
        self.game_name = game_name
        self.game_developer = game_developer
        self.game_id = game_id
        self._xyCords = xyCords
        self.trigger_menu_func = trigger_menu_func
        self.setObjectName("GameFrameWidget")

        if winaccent.system_uses_light_theme:
            self.lighter_text_color = "#4d4d4d"
            self.darker_text_color = "#242424"
        else:
            self.lighter_text_color = "#f0f0f0"
            self.darker_text_color = "#c3c3c3"

        self.generateIcons()
        self.setLayout(self.grid_layout)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.draw()
    
    def generateIcons(self):
        
        game_icon_pil = Image.open(self.game_icon)
        game_icon_pil = game_icon_pil.resize((600,900))

        self.game_pixmap = QPixmap(self.game_icon)
        self.game_pixmap = self.game_pixmap.scaled(QSize(250,400),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation)

        return
    
    def draw(self):

        self.game_label = ClickableLabelGame(
            self.label_clicked, text="game_icon", xyCords=self._xyCords, 
            game=self.game_name, game_id=self.game_id, icon_path=self.game_icon
        )

        self.game_label.setPixmap(self.game_pixmap)
        self.game_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.game_label,0,0)

        vertical_spacer = QSpacerItem(20,10,QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.grid_layout.addItem(vertical_spacer)

        self.game_name_label = QLabel(self.game_name)
        self.game_name_label.setFont(QFont("IBM 3270", 16))
        p = self.game_name_label.palette()
        p.setColor(self.game_name_label.foregroundRole(), QColor(self.darker_text_color))
        self.game_name_label.setPalette(p)
        self.game_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.game_name_label,2,0)

        self.game_developer_label = QLabel(self.game_developer)
        self.game_developer_label.setFont(QFont("IBM 3270", 12))
        p = self.game_developer_label.palette()
        p.setColor(self.game_developer_label.foregroundRole(), QColor(self.lighter_text_color))
        self.game_developer_label.setPalette(p)
        self.game_developer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.game_developer_label,3,0)

        return
    
    def label_clicked(self, event, data):
        button = event.button()
        modifiers = event.modifiers()
        if modifiers == Qt.KeyboardModifier.NoModifier and button == Qt.MouseButton.LeftButton:
            Game.SelectGame(data)
            Cache.SetupCache()
            Launch.SetStartupGame()
            self.trigger_menu_func()