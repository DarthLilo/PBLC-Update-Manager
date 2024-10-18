from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QEvent

class ClickableLabel(QLabel):
    """Activates a function \"whenClicked\" when the label is clicked and transmits the event and an dictionary package of data!"""
    def __init__(self, whenClicked, hoverEvent=None, parent=None, xyCords=(0,0), author="Author", name="Name", version="1.0.0", **kwargs):
        QLabel.__init__(self,parent,**kwargs)
        self._whenClicked = whenClicked
        self._hoverEvent = hoverEvent
        self._xyCords = xyCords
        self._author = author
        self._name = name
        self._version = version
        if callable(hoverEvent):
            self.installEventFilter(self)
    
    def eventFilter(self, object, event):
        if event.type() == QEvent.Type.Enter:
            self._hoverEvent(True)
            return True
        elif event.type() == QEvent.Type.Leave:
            self._hoverEvent(False)
        return False
    
    def mouseReleaseEvent(self, event):
        self._whenClicked(event, {
            "author": self._author,
            "name": self._name,
            "version": self._version,
            "xyCords": self._xyCords
        })