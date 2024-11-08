from PyQt6.QtCore import QSize, Qt, pyqtProperty, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QFrame, QSpacerItem, QHBoxLayout, QCompleter, QComboBox, QPushButton, QDialog, QDialogButtonBox, QFileDialog
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont, QPixmap, QColor

from .LethalRunning import LethalRunning
from ..Assets import Assets
from ..Launch import Launch
from ..Modpacks import Modpacks
from ..Filetree import Filetree
from .ClickableLabel import ClickableLabel
from PIL import Image, ImageQt
from packaging import version

import os, winaccent, winsound

class ModpackInfoFrame(QFrame):
    def __init__(self,modpack_name,modpack_author,modpack_version,mod_count,modpack_icon_pixmap,back_event):
        super().__init__()

        self._modpack_name = modpack_name
        self._modpack_author = modpack_author
        self._modpack_version = modpack_version
        self._mod_count = mod_count
        self.modpack_icon_pixmap = modpack_icon_pixmap
        self.modpack_icon_pixmap_zoomed = None
        self._back_event = back_event

        if winaccent.system_uses_light_theme:
            self.main_theme_color = "#242424"
        else:
            self.main_theme_color = "#c3c3c3"

        self.GenIcons()

        self.modpack_info_layout = QVBoxLayout()
        self.draw()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Expanding)
        self.setLayout(self.modpack_info_layout)

    def GenIcons(self):
        self.modpack_icon_pixmap_zoomed = Assets.CropCenter(self.modpack_icon_pixmap,1.2)
    
    def draw(self):
        
        self.modpack_icon_label = ClickableLabel(self.SelectIcon,hoverEvent=self.HoverEventIcon)
        self.modpack_icon_label.setPixmap(self.modpack_icon_pixmap.scaled(QSize(200,200),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation))
        self.modpack_icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.modpack_info_layout.addWidget(self.modpack_icon_label)

        self.modpack_name_label = QLabel(self._modpack_name)
        self.modpack_name_label.setFont(QFont("IBM 3270", 25))
        self.modpack_name_label.setContentsMargins(0,10,0,0)
        self.modpack_name_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.modpack_info_layout.addWidget(self.modpack_name_label)

        self.modpack_author_version = ClickableLabel(self.EditVersion,text=f"{self._modpack_author} - {self._modpack_version}", hoverEvent=self.VersionHover) #QLabel(f"{self._modpack_author} - {self._modpack_version}")
        self.modpack_author_version.setFont(QFont("IBM 3270", 12))
        self.modpack_author_version.setContentsMargins(0,8,0,0)
        self.modpack_author_version.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.modpack_author_version_grey = self.modpack_author_version.palette()
        self.modpack_author_version_hover = self.modpack_author_version.palette()
        self.modpack_author_version_grey.setColor(self.modpack_author_version.foregroundRole(), QColor(self.main_theme_color))
        self.modpack_author_version_hover.setColor(self.modpack_author_version.foregroundRole(), QColor("#39a7ff"))
        self.modpack_author_version.setPalette(self.modpack_author_version_grey)
        self.modpack_info_layout.addWidget(self.modpack_author_version)

        self.modpack_info_line = QFrame()
        self.modpack_info_line.setGeometry(QRect(320,150,118,3))
        self.modpack_info_line.setFrameShape(QFrame.Shape.HLine)
        self.modpack_info_layout.addWidget(self.modpack_info_line)

        self.launch_modpack_button = QPushButton()
        self.launch_modpack_button.setIcon(QIcon(Assets.getResource(Assets.IconTypes.play,True)))
        self.launch_modpack_button.setIconSize(QSize(40,40))
        self.modpack_info_layout.addWidget(self.launch_modpack_button)

        self.quick_action_container = QWidget()
        self.quick_action_layout = QHBoxLayout(self.quick_action_container)
        self.open_modpack_dir = QPushButton()
        self.update_modpack = QPushButton()
        self.delete_modpack = QPushButton()

        self.open_modpack_dir.setIcon(QIcon(Assets.getResource(Assets.IconTypes.folder,True)))
        self.update_modpack.setIcon(QIcon(Assets.getResource(Assets.IconTypes.refresh,True)))
        self.delete_modpack.setIcon(QIcon(Assets.getResource(Assets.IconTypes.trash_can,True)))

        self.open_modpack_dir.setIconSize(QSize(35,35))
        self.update_modpack.setIconSize(QSize(35,35))
        self.delete_modpack.setIconSize(QSize(35,35))

        self.quick_action_layout.addWidget(self.open_modpack_dir)
        self.quick_action_layout.addWidget(self.update_modpack)
        self.quick_action_layout.addWidget(self.delete_modpack)
        self.modpack_info_layout.addWidget(self.quick_action_container)

        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.modpack_info_layout.addItem(spacer)

        self.mod_count_label = QLabel(f"({self._mod_count}) Mods")
        self.mod_count_label.setFont(QFont("IBM 3270", 12))
        self.mod_count_label.setContentsMargins(0,8,0,0)
        self.mod_count_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.mod_count_label_grey = self.mod_count_label.palette()
        self.mod_count_label_grey.setColor(self.mod_count_label.foregroundRole(), QColor(self.main_theme_color))
        self.mod_count_label.setPalette(self.mod_count_label_grey)
        self.modpack_info_layout.addWidget(self.mod_count_label)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.goBackInteract)
        self.modpack_info_layout.addWidget(self.back_button)

        self.launch_modpack_button.clicked.connect(lambda: Launch.Start(self._modpack_author,self._modpack_name))
        self.open_modpack_dir.clicked.connect(self.openModpackFolder)
        self.update_modpack.clicked.connect(self.updateModpack)
        self.delete_modpack.clicked.connect(self.deleteModpack)
    
    def SelectIcon(self, event, _):
        self.OpenFilepathDialog()
    
    def HoverEventIcon(self, hover):
        if hover:
            self.modpack_icon_label.setPixmap(self.modpack_icon_pixmap_zoomed)
        else:
            self.modpack_icon_label.setPixmap(self.modpack_icon_pixmap)
    
    def EditVersion(self, event, _):
        dlg = EditVersion()
        result = dlg.exec()
        if result:
            self._modpack_version = dlg.new_version.text()
            self.modpack_author_version.setText(f"{self._modpack_author} - {self._modpack_version}")
            json = Modpacks.GetJson(self._modpack_author,self._modpack_name)
            json['version'] = dlg.new_version.text()
            Modpacks.WriteJson(self._modpack_author,self._modpack_name,json)
    
    def VersionHover(self, hover):
        if hover:
            self.modpack_author_version.setPalette(self.modpack_author_version_hover)
        else:
            self.modpack_author_version.setPalette(self.modpack_author_version_grey)


    def OpenFilepathDialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self,"Open File","","Image Files (*.png)")
        if file_name:
            new_pixmap = QPixmap(file_name).scaled(QSize(200,200),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation)
            self.modpack_icon_label.setPixmap(new_pixmap)
            self.modpack_icon_pixmap = new_pixmap
            Modpacks.CopyIcon(self._modpack_author,self._modpack_name,file_name)
            self.GenIcons()
        return

    def setModCount(self, value):
        self.mod_count_label.setText(f"({value}) Mods")
    
    def openModpackFolder(self):
        os.startfile(Modpacks.Path(self._modpack_author,self._modpack_name))
    
    def updateModpack(self):
        if not Filetree.IsLethalRunning(LethalRunning):
            dlg = ConfirmUpdate("Check for and install updates if available?")
            result = dlg.exec()
            if result:
                Modpacks.UpdateVerify(self._modpack_author,self._modpack_name)
                Modpacks.DeselectModpack()
    
    def deleteModpack(self):
        if not Filetree.IsLethalRunning(LethalRunning):
            dlg = ConfirmUpdate("Are you sure you want to delete this modpack?")
            result = dlg.exec()
            if result:
                Modpacks.DeselectModpack()
                Modpacks.Delete(self._modpack_author,self._modpack_name)
                self.goBackInteract()
    
    def goBackInteract(self):
        self._back_event()
    
    def setModpackData(self, modpack_name, modpack_author, modpack_version, mod_count, modpack_icon_pixmap):
        self._modpack_name = modpack_name
        self.modpack_name_label.setText(modpack_name)

        self._modpack_author = modpack_author
        self._modpack_version = modpack_version
        self.modpack_author_version.setText(f"{self._modpack_author} - {self._modpack_version}")

        self._mod_count = mod_count
        self.mod_count_label.setText(f"({self._mod_count}) Mods")

        self.modpack_icon_pixmap = modpack_icon_pixmap
        self.modpack_icon_label.setPixmap(self.modpack_icon_pixmap.scaled(QSize(200,200),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation))

        self.GenIcons()

class ConfirmUpdate(QDialog):
    def __init__(self,message):
        super().__init__()

        self.setWindowTitle("Modpack Update")
        self.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))

        Buttons = (
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        self.button_box = QDialogButtonBox(Buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        self.message = QLabel(message)
        layout.addWidget(self.message)
        layout.addWidget(self.button_box)

class EditVersion(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("New Version")
        self.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))

        Buttons = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box = QDialogButtonBox(Buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        self.message = QLabel("New Version")
        self.new_version = QLineEdit()
        self.new_version.setPlaceholderText("1.0.0")
        layout.addWidget(self.message)
        layout.addWidget(self.new_version)
        layout.addWidget(self.button_box)

    def accept(self):
        try:
            version.Version(self.new_version.text())
            super().accept()
        except version.InvalidVersion:
            winsound.PlaySound('SystemAsterisk',winsound.SND_ASYNC)
            return
        