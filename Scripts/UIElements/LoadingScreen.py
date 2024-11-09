from PyQt6.QtCore import QSize, Qt, pyqtProperty, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QFrame, QSpacerItem, QHBoxLayout, QCompleter, QComboBox, QPushButton, QTabBar, QFileDialog, QToolTip, QScrollArea, QLayout
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont, QPixmap, QColor

from ..Assets import Assets

class LoadingScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self._layout = QGridLayout(self)

        self.loading_anim_label = QLabel()
        self.loading_anim = QMovie(Assets.getResource(Assets.ResourceTypes.loading_screen, True))
        self.loading_anim_label.setMovie(self.loading_anim)
        self.loading_anim.start()
        self.loading_anim_label.setFixedSize(QSize(400,400))
        self.loading_anim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_anim_label.setScaledContents(True)
        self._layout.addWidget(self.loading_anim_label)