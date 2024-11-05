from PyQt6.QtWidgets import QLabel, QMenu
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QEvent

from ..Assets import Assets
from ..Launch import Launch
from ..Modpacks import Modpacks

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
        play_action.setIcon(QIcon(Assets.getResource(Assets.IconTypes.play)))
        play_action.triggered.connect(lambda: Launch.Start(self._author,self._name))

        edit_action = QAction("Edit", self)
        edit_action.setIcon(QIcon(Assets.getResource(Assets.IconTypes.edit)))
        edit_action.triggered.connect(lambda: self._edit_screen_func(self.click_data,update_modcount_func=self.parent().UpdateFrameModCount))

        delete_action = QAction("Delete", self)
        delete_action.setIcon(QIcon(Assets.getResource(Assets.IconTypes.trash_can)))
        delete_action.triggered.connect(self.deleteModpack)
        
        context_menu.addAction(play_action)
        context_menu.addAction(edit_action)
        context_menu.addAction(delete_action)

        context_menu.exec(event.globalPos())
    
    def deleteModpack(self):
        Modpacks.Delete(self._author,self._name)
        Modpacks.RefreshModpacks()

    
    def mouseReleaseEvent(self, event):
        self._whenClicked(event, self.click_data)