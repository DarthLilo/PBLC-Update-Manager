from PyQt6.QtCore import QSize, Qt, pyqtProperty, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QFrame, QSpacerItem, QHBoxLayout, QCompleter, QComboBox, QPushButton, QDialog, QDialogButtonBox
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont, QPixmap, QColor

from .ModListScrollMenu import ModListSrollMenu
from .ModpackInfoFrame import ModpackInfoFrame
from ..Assets import Assets
from ..Modpacks import Modpacks

import os

class EditModpackMenu(QWidget):
    def __init__(self,modpack_icon="", modpack_name="Modpack",modpack_author="Author",modpack_version="1.0.0",mod_count=0,back_event=None,update_modcount_func=None):
        super().__init__()
        self._layout = QGridLayout()
        self.setLayout(self._layout)
        self.modpack_icon = modpack_icon
        self.generateIcons()
        self.modpack_author = modpack_author
        self.modpack_name = modpack_name
        self.mod_count = mod_count
        self._update_modcount_func = update_modcount_func

        
        self.modpack_info_frame = ModpackInfoFrame(modpack_name,modpack_author,modpack_version,mod_count,self.modpack_icon_pixmap,back_event)

        self.mod_list_frame = ModListSrollMenu()
        for mod in Modpacks.ListMods(modpack_author,modpack_name):
            self.mod_list_frame.addMod(mod['icon_path'],mod['name'],mod['author'],mod['mod_version'])
        self.mod_list_frame.addSpacer()


        self.mod_search_frame_layout = QHBoxLayout()
        self.mod_search_frame = QFrame()
        self.mod_search_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.mod_search_frame.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)

        self.search_filters = QComboBox()
        self.search_bar = QLineEdit()
        self.add_mod = QPushButton()
        self.export_modpack = QPushButton()
        self.check_for_updates = QPushButton()
        self.search_bar.setPlaceholderText("Search Mods...")
        self.search_bar.textChanged.connect(self.updateModList)
        self.search_bar.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.mod_search_frame_layout.addWidget(self.search_filters)
        self.mod_search_frame_layout.addWidget(self.search_bar)
        self.mod_search_frame_layout.addWidget(self.export_modpack)
        self.mod_search_frame_layout.addWidget(self.check_for_updates)
        self.mod_search_frame_layout.addWidget(self.add_mod)
        self.mod_search_frame.setLayout(self.mod_search_frame_layout)

        self.search_filters.addItems(["All","Updatable","Disabled"])
        self.search_filters.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Expanding)
        self.search_filters.currentTextChanged.connect(self.updateModFilters)

        self.search_completer = QCompleter(self.mod_list_frame.getModNames())
        self.search_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_bar.setCompleter(self.search_completer)

        self.add_mod.setIcon(QIcon(Assets.getResource(Assets.IconTypes.plus)))
        self.add_mod.setIconSize(QSize(40,40))

        self.export_modpack.setIcon(QIcon(Assets.getResource(Assets.IconTypes.archive)))
        self.export_modpack.setIconSize(QSize(40,40))

        self.check_for_updates.setIcon(QIcon(Assets.getResource(Assets.IconTypes.download)))
        self.check_for_updates.setIconSize(QSize(40,40))


        self.check_for_updates.clicked.connect(self.CheckForUpdates)
        self.export_modpack.clicked.connect(self.ExportModpack)
        self.add_mod.clicked.connect(self.AddMod)


        #mod_search_frame.setStyleSheet("""
        #QFrame {
        #    background: #002025;
        #    border-radius: 40px;
        #    opacity: 100;
        #    border: 2px solid #ff2025;
        #}
        #""")


        self._layout.addWidget(self.modpack_info_frame,0, 0, 7, 1)
        self._layout.addWidget(self.mod_list_frame,1,1,6,3)
        self._layout.addWidget(self.mod_search_frame,0,1,1,3)
    
    def AddMod(self):
        add_mod_dialog = AddModInputDialog()
        result = add_mod_dialog.exec()
        if result:
            Modpacks.Mods.Add(add_mod_dialog.mod_import_field.text())
    
    def RedrawModFrames(self):
        self.deleteAllModFrames()
        for mod in Modpacks.ListMods(self.modpack_author,self.modpack_name):
            self.mod_list_frame.addMod(mod['icon_path'],mod['name'],mod['author'],mod['mod_version'])
        self.mod_list_frame.addSpacer()

        new_mod_count = Modpacks.GetModCount(self.modpack_author,self.modpack_name)
        self.modpack_info_frame.setModCount(new_mod_count)
        self._update_modcount_func(new_mod_count)

    def CheckForUpdates(self):
        Modpacks.ScanForUpdates()
        
        self.RedrawModFrames()

    def ExportModpack(self):
        Modpacks.Export(self.modpack_author,self.modpack_name)
        
        ConfirmPopup = QDialog()
        ConfirmPopup.setWindowTitle("Export")
        ConfirmPopup.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Export finished!"))
        buttons_box = (QDialogButtonBox.StandardButton.Ok)
        buttons = QDialogButtonBox(buttons_box)
        buttons.accepted.connect(ConfirmPopup.accept)
        layout.addWidget(buttons)
        ConfirmPopup.setLayout(layout)
        ConfirmPopup.exec()

    def generateIcons(self):
        if os.path.exists(self.modpack_icon):
            modpack_icon_path = self.modpack_icon
        else:
            modpack_icon_path = Assets.getResource(Assets.IconTypes.missing)
        
        self.modpack_icon_pixmap = QPixmap(modpack_icon_path).scaled(QSize(200,200),aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,transformMode=Qt.TransformationMode.SmoothTransformation)
    
    def updateModList(self, text):
        
        for mod in self.mod_list_frame.getMods():
            if text.lower() in mod.mod_name.lower():
                mod.show()
            else:
                mod.hide()
    
    def updateModFilters(self, event):
        if str(event) != "All":
            for mod in self.mod_list_frame.getMods():
                mod.update_filter(str(event))
            
        else:
            for mod in self.mod_list_frame.getMods():
                mod.inFilter = True
                mod.curFilter = "All"
                mod.determine_visibility()
    
    def deleteAllModFrames(self):
        mod_removal_list = []
        for mod in self.mod_list_frame.getMods():
            mod.Delete(remove_container=False)
            mod_removal_list.append(mod)
        
        for mod in mod_removal_list:
            self.mod_list_frame.removeMod(mod)
    
    def ShowNewModpack(self,modpack_icon="", modpack_name="Modpack",modpack_author="Author",modpack_version="1.0.0",mod_count=0):
        self.modpack_icon = modpack_icon
        self.generateIcons()

        self.modpack_info_frame.setModpackData(modpack_name,modpack_author,modpack_version,mod_count,self.modpack_icon_pixmap)
        self.deleteAllModFrames()

        for mod in Modpacks.ListMods(modpack_author,modpack_name):
            self.mod_list_frame.addMod(mod['icon_path'],mod['name'],mod['author'],mod['mod_version'])
        self.mod_list_frame.addSpacer()

class AddModInputDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Mod")
        self.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))

        Buttons = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box = QDialogButtonBox(Buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        self.mod_import_field = QLineEdit()
        self.mod_import_field.setPlaceholderText("Thunderstore URL")
        layout.addWidget(self.mod_import_field)
        layout.addWidget(self.button_box)