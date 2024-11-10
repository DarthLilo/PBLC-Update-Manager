from PyQt6.QtCore import (
    Qt, QSize, QObject, pyqtSignal)

from PyQt6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy, QHBoxLayout, QSpacerItem, QWidget, QPushButton, QDialog, QDialogButtonBox, QVBoxLayout, QScrollArea
from PyQt6.QtGui import QColor, QPalette, QPixmap, QFont, QIcon

from .ClickableLabel import ClickableLabel
from .AnimatedToggle import AnimatedToggle
from .LethalRunning import LethalRunning
from ..Assets import Assets
from ..Modpacks import Modpacks
from ..Cache import Cache
from ..Networking import Networking
from ..Filetree import Filetree

import os, random, threading, winaccent

class ModFrame(QFrame):
    def __init__(self, parent=None, mod_icon="", mod_name="Mod",mod_author="Author",mod_version="1.0.0",delete_func=None):
        super().__init__()
        self._mod_json = Modpacks.Mods.Json(mod_author,mod_name)
        self._layout = QHBoxLayout()
        self.mod_icon = mod_icon
        self.mod_name = mod_name
        self.mod_author = mod_author
        self.mod_version = mod_version
        self.mod_update_version = self._mod_json['has_updates']
        self.mod_enabled = self._mod_json['enabled']
        self.updateable = bool(self._mod_json['has_updates'])
        self.inSearch = True
        self.inFilter = True
        self.curFilter = "All"
        self._delete_func = delete_func

        if winaccent.system_uses_light_theme:
            self.main_theme_color = "#242424"
        else:
            self.main_theme_color = "#c3c3c3"

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
            mod_icon_path = Assets.getResource(Assets.IconTypes.missing)
        
        self._mod_icon_pixmap = QPixmap(mod_icon_path).scaled(QSize(80,80),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation)
    
    def draw(self):
        self.mod_icon_label = QLabel("mod_icon")
        self.mod_icon_label.setPixmap(self._mod_icon_pixmap)
        self.mod_icon_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(self.mod_icon_label)

        # Mod Data

        self.mod_data_container = QScrollArea()
        self.mod_data_container.setStyleSheet("""
            QScrollArea {
                border: none;
                outline: none;
                background: transparent;
            }
            QScrollBar {
                border: none;
            }
        """)
        self.mod_data_container.setMaximumHeight(80)
        self.mod_data_container.setAlignment(Qt.AlignmentFlag.AlignLeft)
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
            self.version_color = self.main_theme_color

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
        self.mod_author_label_grey.setColor(self.mod_version_label.foregroundRole(), QColor(self.main_theme_color))
        self.mod_author_label.setPalette(self.mod_author_label_grey)
        self.mod_data_layout.addWidget(self.mod_author_label,1,0)
        self._layout.addWidget(self.mod_data_container)

        #spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #self._layout.addItem(spacer)

        # Actions

        self.mod_toggle = AnimatedToggle(squish_amount=2.5)
        self.mod_toggle.setChecked(self.mod_enabled)
        self._layout.addWidget(self.mod_toggle,alignment=Qt.AlignmentFlag.AlignRight)
        self.mod_toggle.stateChanged.connect(self.update_state)

        self.refresh_mod = QPushButton()
        self.refresh_mod.setIcon(QIcon(Assets.getResource(Assets.IconTypes.refresh,True)))
        self.refresh_mod.setIconSize(QSize(30,30))
        self.refresh_mod.clicked.connect(self.CheckForUpdates)
        self._layout.addWidget(self.refresh_mod,alignment=Qt.AlignmentFlag.AlignRight)
        

        self.delete_mod = QPushButton()
        self.delete_mod.setIcon(QIcon(Assets.getResource(Assets.IconTypes.trash_can,True)))
        self.delete_mod.clicked.connect(self.DeleteMod)
        self.delete_mod.setIconSize(QSize(30,30))
        self._layout.addWidget(self.delete_mod,alignment=Qt.AlignmentFlag.AlignRight)
    
    def update_state(self, event):
        
        if Filetree.IsLethalRunning(LethalRunning):
            return
        
        Modpacks.Mods.Toggle(self.mod_author,self.mod_name)
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
            Networking.OpenURL(f"https://thunderstore.io/c/lethal-company/p/{data['author']}/{data['name']}/")
        return
    
    def HoverEvent(self, hover):
        if hover:
            self.mod_name_label.setPalette(self.mod_name_label_hover)
        else:
            self.mod_name_label.setPalette(self.mod_name_label_defualt)
    
    def CheckForUpdates(self):
        if Filetree.IsLethalRunning(LethalRunning):
            return
        
        has_updates = Modpacks.Mods.CheckForUpdates(self.mod_author,self.mod_name)
        if has_updates:
            self.mod_update_version = Cache.Get(self.mod_author,self.mod_name)['version_number']
            self.updateable = True
            Modpacks.Mods.SetUpdateVersion(self.mod_author,self.mod_name,self.mod_update_version)
            self.mod_version_label.setText(f"({self.mod_version}    <    {self.mod_update_version})")
            self.mod_version_label_grey.setColor(self.mod_version_label.foregroundRole(), QColor("#57ff7e"))
            self.mod_version_label.setPalette(self.mod_version_label_grey)
            upd_dialog = UpdateDialog(self.mod_author,self.mod_name,self.mod_version,self.mod_update_version)
            result = upd_dialog.exec()

            if result:
                Modpacks.CacheLoadingScreenFunc()
                Modpacks.SetCacheStatus(f"Downloading {self.mod_author}-{self.mod_name}")
                #Modpacks.Mods.Update(self.mod_author,self.mod_name,self.mod_update_version)
                self.updateable = False
                Modpacks.Mods.SetUpdateVersion(self.mod_author,self.mod_name,False)
                self.mod_version_label.setText(f"({self.mod_update_version})")
                self.mod_version_label_grey.setColor(self.mod_version_label.foregroundRole(), QColor(self.main_theme_color))
                self.mod_version_label.setPalette(self.mod_version_label_grey)
                self.mod_version = self.mod_update_version

                self.UpdateMod(self.mod_author,self.mod_name,self.mod_version)
                #update_worker_object = UpdateWorkerObject()
                #update_worker_object.progress_update.connect()
                #update_worker_object.finished.connect(Modpacks.CacheToModpack)

                #update_worker_thread = threading.Thread(target=lambda :update_worker_object.run(self.mod_author,self.mod_name,self.mod_version),daemon=True)
                #update_worker_thread.start()
    
    def UpdateMod(self,author,name,version):

        Modpacks.Mods.Update(author,name,version,text_output_func=Modpacks.SetCacheStatus,finished_func=Modpacks.CacheToModpack)
    
    def DeleteMod(self):
        if Filetree.IsLethalRunning(LethalRunning):
            return
        
        Modpacks.Mods.Delete(self.mod_author,self.mod_name,self.mod_version)
        self.Delete()
    
    def Delete(self, s=None, remove_container = True):
        parent_layout = self.parent().layout()
        parent_layout.removeWidget(self)
        if remove_container:
            self._delete_func(self)
        self.deleteLater()
        
        del self

class UpdateWorkerObject(QObject):
    progress_update = pyqtSignal(str)
    finished = pyqtSignal()
    
    def run(self,author,name,version):
        Modpacks.Mods.Update(author,name,version,text_output_func=self.progress_update.emit)
        self.finished.emit()

class UpdateDialog(QDialog):
    def __init__(self,author,name,old_version,new_version):
        super().__init__()

        self.setWindowTitle("Mod Updater")
        self.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))

        QButtons = (
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )

        self.button_box = QDialogButtonBox(QButtons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        display_message = QLabel(f"{author}-{name} has a new version available! {old_version} < {new_version}\n\nWould you like to update?")
        layout.addWidget(display_message)
        layout.addWidget(self.button_box)
        self.setLayout(layout)