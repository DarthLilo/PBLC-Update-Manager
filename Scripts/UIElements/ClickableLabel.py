from PyQt6.QtWidgets import QLabel, QMenu, QDialog, QDialogButtonBox, QVBoxLayout, QLineEdit, QPushButton, QFileDialog
from PyQt6.QtGui import QAction, QIcon, QCursor
from PyQt6.QtCore import QEvent, Qt

from .LethalRunning import LethalRunning
from ..Assets import Assets
from ..Launch import Launch
from ..Modpacks import Modpacks
from ..Filetree import Filetree
from ..Logging import Logging
from ..Util import Util

import winsound, os

class ClickableLabel(QLabel):
    """Activates a function \"whenClicked\" when the label is clicked and transmits the event and an dictionary package of data!"""
    def __init__(self, whenClicked, 
                 hoverEvent=None, parent=None, 
                 xyCords=(0,0), author="Author", 
                 name="Name", version="1.0.0", 
                 icon_path="",mod_count=0, 
                 modpack_context_menu=False, 
                 edit_screen_func = None, **kwargs):
        QLabel.__init__(self,parent,**kwargs)
        self._whenClicked = whenClicked
        self._hoverEvent = hoverEvent
        self._xyCords = xyCords
        self._author = author
        self._name = name
        self._version = version
        self._icon_path = icon_path
        self._mod_count = mod_count
        self._modpack_context_menu = modpack_context_menu
        self._edit_screen_func = edit_screen_func
        self.default_cursor = self.cursor()
        self.hover_cursor = QCursor(Qt.CursorShape.PointingHandCursor)
        self.click_data = {
            "author": self._author,
            "name": self._name,
            "version": self._version,
            "icon": self._icon_path,
            "mod_count": self._mod_count,
            "xyCords": self._xyCords
        }
        if callable(hoverEvent):
            self.installEventFilter(self)
    
    def enterEvent(self, event):
        self.setCursor(self.hover_cursor)
    
    def leaveEvent(self, a0):
        self.setCursor(self.default_cursor)
    
    def eventFilter(self, object, event):
        if event.type() == QEvent.Type.Enter:
            self._hoverEvent(True)
            return True
        elif event.type() == QEvent.Type.Leave:
            self._hoverEvent(False)
        return False
    
    def contextMenuEvent(self, event):

        if not self._modpack_context_menu:
            return

        context_menu = QMenu(self)

        play_action = QAction("Play", self)
        play_action.setIcon(QIcon(Assets.getResource(Assets.IconTypes.play,True)))
        play_action.triggered.connect(lambda: Launch.Start(self._author,self._name))

        play_extra_action = QAction("Play Extra", self)
        play_extra_action.setIcon(QIcon(Assets.getResource(Assets.IconTypes.play,True)))
        play_extra_action.triggered.connect(lambda: Launch.Start(self._author,self._name,True))

        edit_action = QAction("Edit", self)
        edit_action.setIcon(QIcon(Assets.getResource(Assets.IconTypes.edit,True)))
        edit_action.triggered.connect(lambda: self._edit_screen_func(self.click_data,update_modcount_func=self.parent().UpdateFrameModCount))

        update_action = QAction("Update", self)
        update_action.setIcon(QIcon(Assets.getResource(Assets.IconTypes.refresh,True)))
        update_action.triggered.connect(self.updateModpack)

        folder_action = QAction("Folder", self)
        folder_action.setIcon(QIcon(Assets.getResource(Assets.IconTypes.folder,True)))
        folder_action.triggered.connect(self.openFolder)

        verify_action = QAction("Verify", self)
        verify_action.setIcon(QIcon(Assets.getResource(Assets.IconTypes.file,True)))
        verify_action.triggered.connect(self.VerifyModpack)

        delete_action = QAction("Delete", self)
        delete_action.setIcon(QIcon(Assets.getResource(Assets.IconTypes.trash_can,True)))
        delete_action.triggered.connect(self.deleteModpack)
        
        context_menu.addAction(play_action)
        context_menu.addAction(play_extra_action)
        context_menu.addAction(edit_action)
        context_menu.addAction(update_action)
        context_menu.addAction(folder_action)
        context_menu.addAction(verify_action)
        context_menu.addAction(delete_action)

        context_menu.exec(event.globalPos())
    
    def VerifyModpack(self):

        Logging.New("Starting verification process")

        if Modpacks.GetJson(self._author,self._name)['online_link']:
            modpack_data = Util.UrlPathDecoder(Modpacks.GetJson(self._author,self._name)['online_link'])

            Modpacks.Verify(modpack_data)
            return

        dlg = EditVersion()
        result = dlg.exec()
        if result:
            modpack_data = Util.UrlPathDecoder(dlg.new_version.text())

            if not f"{modpack_data['author']}-{modpack_data['name']}" == f"{self._author}-{self._name}":
                Logging.New("Please select a matching modpack file!")
                winsound.PlaySound('SystemAsterisk',winsound.SND_ASYNC)
                return
            
            Modpacks.Verify(modpack_data)


    def deleteModpack(self):
        if Filetree.IsLethalRunning(LethalRunning):
            return
        Modpacks.Delete(self._author,self._name)
        Modpacks.RefreshModpacks()
    
    def openFolder(self):
        os.startfile(Modpacks.Path(self._author,self._name))
    
    def updateModpack(self):
        if not Filetree.IsLethalRunning(LethalRunning):
            dlg = ConfirmUpdate("Check for and install updates if available?")
            result = dlg.exec()
            if result:
                Modpacks.UpdateVerify(self._author,self._name)
                Modpacks.DeselectModpack()

    
    def mouseReleaseEvent(self, event):
        self._whenClicked(event, self.click_data)

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
        self.message = QLabel("Modpack Source")
        self.new_version = QLineEdit()
        self.new_version.setPlaceholderText("Filepath or URL to modpack source")

        self.modpack_source_button = QPushButton()
        self.modpack_source_button.setIcon(QIcon(Assets.getResource(Assets.IconTypes.folder,True)))
        self.modpack_source_button.clicked.connect(self.OpenFilepathDialog)

        layout.addWidget(self.message)
        layout.addWidget(self.new_version)
        layout.addWidget(self.modpack_source_button)
        layout.addWidget(self.button_box)
    
    def OpenFilepathDialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self,"Open File","","Json Files (*.json)")

        if file_name:
            self.new_version.setText(file_name)

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