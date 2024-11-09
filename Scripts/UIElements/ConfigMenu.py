from PyQt6.QtCore import QSize, Qt, pyqtProperty, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QFrame, QSpacerItem, QHBoxLayout, QCompleter, QComboBox, QPushButton, QDialog, QScrollArea, QSpinBox, QFileDialog, QDialogButtonBox
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont, QPixmap, QColor

from .VerticalTab import VerticalTabWidget
from .AnimatedToggle import AnimatedToggle
from ..Assets import Assets
from ..Config import Config

class ConfigMenu(QDialog):
    def __init__(self, parent=None):
        super().__init__()

        self._layout = QGridLayout(self)
        self.categories = {}
        self.setWindowTitle("Config")
        self.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))

        self.active_changes = {}

        
        self.config_menu_selection = QFrame()
        self.config_menu_selection_layout = QGridLayout(self.config_menu_selection)
        self.config_menu_selection.setFrameStyle(QFrame.Shape.StyledPanel)

        #self.config_menu_selection.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        self.config_tab_manager = VerticalTabWidget()

        self.config_menu_selection_layout.addWidget(self.config_tab_manager,0,0,1,2)

        self.save_button = QPushButton("Save")
        self.reset_to_default = QPushButton("Reset to Default")
        self.discard = QPushButton("Discard")
        self.config_menu_selection_layout.addWidget(self.save_button,1,0,1,2)
        self.config_menu_selection_layout.addWidget(self.reset_to_default,2,0,1,1)
        self.config_menu_selection_layout.addWidget(self.discard,2,1,1,1)
        
        self.save_button.clicked.connect(self.ApplyChanges)
        self.discard.clicked.connect(self.CloseConfig)
        self.reset_to_default.clicked.connect(self.ResetConfig)

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

        stylized_name = " ".join(name.split("-")).title()

        self.config_tab_manager.addTab(self.category_scroll_area,stylized_name)
        self.categories[name] = self.category_layout
    
    def addSetting(self, target_category, setting_type, setting_name, description, values=[], cur_value=None):
        if target_category not in self.categories:
            return
        
        if setting_type == "hidden":
            return
        
        setting_frame = QFrame()
        setting_container = QGridLayout(setting_frame)

        styled_setting_name = " ".join(setting_name.split("_")).title()

        setting_name_label_frame = QFrame()
        setting_name_layout = QVBoxLayout(setting_name_label_frame)
        setting_name_label_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        setting_name_label = QLabel(styled_setting_name)
        setting_name_layout.addWidget(setting_name_label)
        setting_name_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        setting_name_label.setFont(QFont("IBM 3270", 16))
        setting_name_label.setContentsMargins(10,0,0,0)
        
        if setting_type == "folder" or setting_type == "file":
            cur_path_label = QLabel(cur_value)
            setting_name_layout.addWidget(cur_path_label)
            cur_path_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            cur_path_label.setFont(QFont("IBM 3270", 8))
            cur_path_label.setContentsMargins(10,0,0,0)
        #setting_name_label_frame.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        setting_description_frame = QFrame()
        setting_description_layout = QHBoxLayout(setting_description_frame)
        setting_description_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        setting_description = QLabel()
        setting_description.setPixmap(QPixmap(Assets.getResource(Assets.IconTypes.info)).scaled(QSize(35,35),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation))
        setting_description.setToolTip(description)
        setting_description_layout.addWidget(setting_description)
        setting_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setting_action_frame = QFrame()
        setting_action_layout = QHBoxLayout(setting_action_frame)
        setting_action_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        setting_action_frame.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        setting_action = None
        
        if setting_type == "bool":
            setting_action = AnimatedToggle(squish_amount=2.5)
            if cur_value: setting_action.setChecked(cur_value == "True")
            setting_action.stateChanged.connect(lambda: self.QueueChange(target_category,setting_name,setting_action.isChecked()))
        
        if setting_type == "folder" or setting_type == "file":
            setting_action = QPushButton(icon=QIcon(Assets.getResource(Assets.IconTypes.folder,True)))
            setting_action.setIconSize(QSize(35,35))
            setting_action.clicked.connect(lambda :self.OpenFileDialog(setting_type,setting_name,target_category,cur_path_label))
            #setting_action = QFileDialog()
        
        if setting_type == "enum":
            setting_action = QComboBox()
            setting_action.addItems(values)
            if cur_value: setting_action.setCurrentIndex(list(values).index(cur_value))
            setting_action.currentTextChanged.connect(lambda: self.QueueChange(target_category,setting_name,setting_action.currentText()))
        
        if setting_type == "int":
            setting_action = QSpinBox()
            setting_action.setMinimum(1)
            setting_action.setMaximum(12)
            if cur_value: setting_action.setValue(int(cur_value))
            setting_action.valueChanged.connect(lambda: self.QueueChange(target_category,setting_name,setting_action.value()))


        if setting_action: setting_action_layout.addWidget(setting_action)
        #setting_action_frame.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        #setting_action.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        
        setting_container.addWidget(setting_name_label_frame,0,1,1,8)
        setting_container.addWidget(setting_description_frame,0,9,1,1)
        setting_container.addWidget(setting_action_frame,0,10,1,1)

        setting_frame.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)

        self.categories[target_category].addWidget(setting_frame)

        return
    
    def OpenFileDialog(self,import_type,setting_name,setting_category,target=None):
        file_name = None
        if import_type == "folder":
            file_name = QFileDialog.getExistingDirectory(self,"Select Folder","")
        elif import_type == "file":
            file_name, _ = QFileDialog.getOpenFileName(self,"Open File","")
        
        if file_name:
            if target: target.setText(file_name)
            self.QueueChange(setting_category,setting_name,file_name)
        return
    
    def QueueChange(self,setting_category,setting_name,value):
        if not setting_category in self.active_changes:
            self.active_changes[setting_category] = {}
        
        self.active_changes[setting_category][setting_name] = value
        print(f"Applied {setting_category}/{setting_name} = {value}")
    
    def ApplyChanges(self):
        #print(self.active_changes)
        for category in self.active_changes:
            for change in self.active_changes[category]:
                Config.Write(category,change,self.active_changes[category][change])
        
        self.CloseConfig()
    
    def CloseConfig(self):
        self.active_changes.clear()
        self.close()
    
    def ResetConfig(self):
        confirm_reset = ConfirmReset()
        result = confirm_reset.exec()

        if result:
            settings_lib = Config.Get()
            for category in settings_lib:
                for option in settings_lib[category]:
                    self.QueueChange(category,option,settings_lib[category][option]['default'])

            self.ApplyChanges()

class ConfirmReset(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reset Config")
        self.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))

        QButtons = (
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )

        self.button_box = QDialogButtonBox(QButtons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        display_message = QLabel("Are you sure you want to reset the config back to default?")
        layout.addWidget(display_message)
        layout.addWidget(self.button_box)
        self.setLayout(layout)