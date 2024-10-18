from PyQt6.QtCore import QSize, Qt, pyqtProperty, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QFrame, QSpacerItem, QHBoxLayout, QCompleter, QComboBox, QPushButton, QTabBar, QFileDialog, QToolTip, QScrollArea
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont, QPixmap, QColor

from .VerticalTab import VerticalTabWidget
from .AnimatedToggle import AnimatedToggle

class ConfigMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self._layout = QGridLayout(self)
        self.categories = {}

        
        self.config_menu_selection = QFrame()
        self.config_menu_selection_layout = QGridLayout(self.config_menu_selection)
        self.config_menu_selection.setFrameStyle(QFrame.Shape.StyledPanel)

        #self.config_menu_selection.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        self.config_tab_manager = VerticalTabWidget()

        self.config_menu_selection_layout.addWidget(self.config_tab_manager,0,0,1,2)

        self.save_button = QPushButton("Save")
        self.reset_to_default = QPushButton("Reset to Default")
        self.discord = QPushButton("Discard")
        self.config_menu_selection_layout.addWidget(self.save_button,1,0,1,2)
        self.config_menu_selection_layout.addWidget(self.reset_to_default,2,0,1,1)
        self.config_menu_selection_layout.addWidget(self.discord,2,1,1,1)

        self._layout.addWidget(self.config_menu_selection,0,0,1,1)

        
    
    def addSpacer(self, target_category):
        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.categories[target_category].addItem(spacer)
    
    def addCategory(self,name):
        self.category_scroll_area = QScrollArea()
        self.category_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.category_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        vscrollbar = self.category_scroll_area.verticalScrollBar()
        vscrollbar.setSingleStep(5)
        self.category_scroll_area.setWidgetResizable(True)

        self.category_container = QFrame()
        self.category_layout = QGridLayout(self.category_container)
        self.category_scroll_area.setWidget(self.category_container)

        self.config_tab_manager.addTab(self.category_scroll_area,name)
        self.categories[name] = self.category_layout
    
    def addSetting(self, target_category, setting_type, setting_name, description, values=[]):
        if target_category not in self.categories:
            return
        
        if setting_type == "hidden":
            return
        
        setting_frame = QFrame()
        setting_container = QGridLayout(setting_frame)

        setting_name_label_frame = QFrame()
        setting_name_layout = QHBoxLayout(setting_name_label_frame)
        setting_name_label_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        setting_name_label = QLabel(setting_name)
        setting_name_layout.addWidget(setting_name_label)
        setting_name_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        setting_name_label.setFont(QFont("IBM 3270", 16))
        setting_name_label.setContentsMargins(10,0,0,0)
        #setting_name_label_frame.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        setting_description_frame = QFrame()
        setting_description_layout = QHBoxLayout(setting_description_frame)
        setting_description_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        setting_description = QLabel()
        setting_description.setPixmap(QPixmap("E:\\Lilos Coding\\PBML\\assets\\info.png").scaled(QSize(35,35),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation))
        setting_description.setToolTip(description)
        setting_description_layout.addWidget(setting_description)
        setting_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setting_action_frame = QFrame()
        setting_action_layout = QHBoxLayout(setting_action_frame)
        setting_action_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        setting_action_frame.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        
        if setting_type == "bool":
            setting_action = AnimatedToggle(squish_amount=2.5)
            setting_action_layout.addWidget(setting_action)
        
        if setting_type == "folder" or setting_type == "file":
            setting_action = QPushButton(icon=QIcon("E:\\Lilos Coding\\PBML\\assets\\folder.png"))
            setting_action.setIconSize(QSize(35,35))
            #setting_action = QFileDialog()
            setting_action_layout.addWidget(setting_action)
        
        if setting_type == "enum":
            setting_action = QComboBox()
            setting_action.addItems(values)
            setting_action_layout.addWidget(setting_action)
        #setting_action_frame.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        #setting_action.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        
        setting_container.addWidget(setting_name_label_frame,0,1,1,8)
        setting_container.addWidget(setting_description_frame,0,9,1,1)
        setting_container.addWidget(setting_action_frame,0,10,1,1)

        setting_frame.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)

        self.categories[target_category].addWidget(setting_frame)

        return
        
