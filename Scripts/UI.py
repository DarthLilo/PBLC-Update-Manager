from PyQt6.QtCore import QSize, Qt, pyqtProperty, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QLineEdit, QLabel, QStackedWidget, QDialog, QDialogButtonBox
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase, QFont

from . import UIElements
from . import Modpacks

from .Assets import Assets
from .Logging import Logging
from .Cache import Cache
from .Config import Config
from .Networking import Networking

import time, random, threading, os

class UI(QWidget):
    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self.LoadFonts()

        self.screen_container = QStackedWidget()
        self._layout.addWidget(self.screen_container)


        # Screens
        self._screen_loading = None
        self._screen_loading_cache_update = UIElements.LoadingScreenCacheUpdate()
        self._screen_modpack_selection = None
        self._screen_edit_modpack = None
        self._screen_add_import_modpack = None
        self._selected_modpack = None
        self._screen_download_threads = UIElements.ModpackDownloadScreen()
        
        Networking.CheckForUpdatesManager()

        #Cache Loading
        if Cache.StartCache:
            self.ShowLoadingScreenCacheUpdate()
            Cache.Update(self.__startup__,self._screen_loading_cache_update.setStatus)
        else:
            self.__startup__()

        
    
    def __startup__(self):
        #Starting
        self.ShowLoadingScreen()
        Modpacks.UpdatePercentageFunc = self.UpdatePercentageBar
        Modpacks.UpdateThreadDisplay = self.UpdateThreadDisplay
        Modpacks.CloseDownloadScreenFunc = self.CloseDownloadScreen
        Modpacks.CacheLoadingScreenFunc = self.ShowLoadingScreenCacheUpdate
        Modpacks.SetGlobalPercent = self._screen_download_threads.setGlobalPercent
        Modpacks.SetCacheStatus = self._screen_loading_cache_update.setStatus
        Modpacks.CacheToModpack = self.CacheToEditModpack
        Modpacks.ShowDownloadScreen = self.ShowDownloadScreen
        Modpacks.ShowLoadingScreen = self.ShowLoadingScreen
        Modpacks.LoadingToEdit = self.LoadingToEditScreen
        Modpacks.DeselectModpack = self.deselectModpack
        Modpacks.RefreshModpacks = self.RefreshModpacks
        Modpacks.ShowModpackSelection = self.ShowModpackSelectionScreen

        launch_worker_object = LaunchWorkerObject()
        launch_worker_object.fadeout_anim.connect(self.FadeToModpackSelection)
        
        launch_thread = threading.Thread(target=launch_worker_object.run,daemon=True).start()
    
    def LoadFonts(self):
        lethal_font = QFontDatabase.addApplicationFont(f"{Assets.asset_folder}/3270-Regular.ttf")
        #families = QFontDatabase.applicationFontFamilies(lethal_font)
    

    def deselectModpack(self):
        self._selected_modpack = None

    # Screen management

    def ShowLoadingScreen(self, prev_menu = None):
        if not self._screen_loading:
            self._screen_loading = UIElements.LoadingScreen()

        if prev_menu:
            self.screen_container.removeWidget(prev_menu)
            Logging.New(f"Removed {prev_menu} from widget stack")

        self.screen_container.removeWidget(self._screen_loading_cache_update)
        self.screen_container.removeWidget(self._screen_edit_modpack)
        self.screen_container.removeWidget(self._screen_modpack_selection)
        self.screen_container.addWidget(self._screen_loading)
        return
    
    def ShowLoadingScreenCacheUpdate(self,status=None):
        
        self.screen_container.removeWidget(self._screen_edit_modpack)
        self.screen_container.removeWidget(self._screen_download_threads)
        self.screen_container.removeWidget(self._screen_modpack_selection)
    
        self.screen_container.addWidget(self._screen_loading_cache_update)

        if status:
            self._screen_loading_cache_update.setStatus(status)
        return
    
    def CacheToEditModpack(self):
        self.screen_container.removeWidget(self._screen_loading_cache_update)

        self.screen_container.addWidget(self._screen_edit_modpack)

    def ShowAddImportModpackScreen(self,type):
        self._screen_add_import_modpack = None
        self._screen_add_import_modpack = UIElements.AddImportModpack(type=type,show_download_screen_func=self.ShowDownloadScreen,update_cache_screen_func=self.ShowLoadingScreenCacheUpdate,cache_status_func=self._screen_loading_cache_update.setStatus,clear_modpack = self.deselectModpack, refresh_modpacks=self.RefreshModpacks)

        self._screen_add_import_modpack.exec()
        #self.screen_container.removeWidget(self._screen_modpack_selection)
        #self.screen_container.addWidget(self._screen_add_import_modpack)

    def CancelAddImportModpackScreen(self):
        self.screen_container.removeWidget(self._screen_add_import_modpack)
        self._screen_add_import_modpack = None
        self.screen_container.addWidget(self._screen_modpack_selection)

    def ShowEditModpackScreen(self, data = None,update_modcount_func=None):
        Modpacks.Select(data['author'],data['name'])
        if not self._screen_edit_modpack:
            self._screen_edit_modpack = UIElements.EditModpackMenu(Assets.modpackIcon(data['icon']),data['name'],data['author'],data['version'],data['mod_count'],self.ShowModpackSelectionScreen,update_modcount_func)
            self._selected_modpack = f"{data['author']}-{data['name']}"
        else:
            if self._selected_modpack != f"{data['author']}-{data['name']}":
                self._screen_edit_modpack.ShowNewModpack(data['icon'],data['name'],data['author'],data['version'],data['mod_count'])
                self._selected_modpack = f"{data['author']}-{data['name']}"
        

        if self._screen_modpack_selection:
            self.screen_container.removeWidget(self._screen_modpack_selection)
            Logging.New(f"Removed {self._screen_modpack_selection} from widget stack")

        self.screen_container.addWidget(self._screen_edit_modpack)
        return
    
    def ShowModpackSelectionScreen(self):
        if not self._screen_modpack_selection:
            self._screen_modpack_selection = UIElements.ModpackSelection(Modpacks.List(),self.ShowEditModpackScreen,self.ShowAddImportModpackScreen)
        
        self.screen_container.removeWidget(self._screen_loading_cache_update)
        self.screen_container.removeWidget(self._screen_edit_modpack)
        self.screen_container.removeWidget(self._screen_loading)
        self.screen_container.addWidget(self._screen_modpack_selection)
        self._screen_modpack_selection.rescanModpacks(Modpacks.List())
        Cache.SelectedModpack = ""

    def FadeToModpackSelection(self, prev_menu=None):
        if not self._screen_modpack_selection:
            self._screen_modpack_selection = UIElements.ModpackSelection(Modpacks.List(),self.ShowEditModpackScreen,self.ShowAddImportModpackScreen)
        
        self.screen_container.removeWidget(self._screen_modpack_selection)
        self.screen_container.removeWidget(self._screen_loading)

        fader = UIElements.FaderWidget(self._screen_loading,self._screen_modpack_selection)
        self.screen_container.addWidget(self._screen_modpack_selection)

        # Modpack download
        if not Modpacks.Exists("DarthLilo","Events Server") and Config.Read("general","auto_download_modpack",'value') == "True":
            dlg = ConfirmDownload("Would you like to install the main modpack?")
            result = dlg.exec()
            if result:
                Modpacks.ImportVerify("https://raw.githubusercontent.com/DarthLilo/PBLC-Update-Manager/refs/heads/master/LiveModpacks/DarthLilo-Events%20Server.json",self.ShowDownloadScreen,self.ShowLoadingScreenCacheUpdate,self._screen_loading_cache_update.setStatus)
                self.deselectModpack()
            else:
                Config.Write("general","auto_download_modpack",False)

    def ShowDownloadScreen(self, prev_menu = None):
        
        if not prev_menu:
            prev_menu = self._screen_modpack_selection
        
        self.screen_container.removeWidget(self._screen_edit_modpack)
        self.screen_container.removeWidget(self._screen_loading_cache_update)
        self.screen_container.removeWidget(prev_menu)
        self.screen_container.addWidget(self._screen_download_threads)
        self._screen_download_threads.initClock()
    
    def RefreshModpacks(self):
        self._screen_modpack_selection.rescanModpacks(Modpacks.List())

    def CloseDownloadScreen(self):
        if not self._screen_modpack_selection:
            self._screen_modpack_selection = UIElements.ModpackSelection(Modpacks.List(),self.ShowEditModpackScreen,self.ShowAddImportModpackScreen)
        self._screen_download_threads.killClock()

        self.screen_container.removeWidget(self._screen_loading_cache_update)
        self.screen_container.removeWidget(self._screen_download_threads)
        self.screen_container.addWidget(self._screen_modpack_selection)
        self._screen_modpack_selection.rescanModpacks(Modpacks.List())

    # Update management

    def LoadingToEditScreen(self):
        self.screen_container.removeWidget(self._screen_loading)
        self.screen_container.addWidget(self._screen_edit_modpack)
        self._screen_edit_modpack.RedrawModFrames()

    def UpdatePercentageBar(self,index,percentage):
        #Logging.New(f"thread [{index}] percentage [{percentage}]")
        self._screen_download_threads.setPercentageBar(index,percentage)
        return
    
    def UpdateThreadDisplay(self,index,author,name,version):
        self._screen_download_threads.setThreadDisplay(index,author,name,version)

    def FinishUpdate(self, prev_screen = None):
        if not self._screen_modpack_selection:
            self._screen_modpack_selection = UIElements.ModpackSelection(Modpacks.List(),self.ShowEditModpackScreen,self.ShowAddImportModpackScreen)
        
        self._screen_modpack_selection.rescanModpacks(Modpacks.List())

        if prev_screen:
            self.screen_container.removeWidget(prev_screen)
        
        self.screen_container.addWidget(self._screen_modpack_selection)

    # Config

    def OpenConfigScreen(self):
        config_menu = UIElements.ConfigMenu()

        config_data = Config.Get()

        for category in config_data:
            config_menu.addCategory(category)

            for option in config_data[category]:
                option_container = config_data[category][option]
                config_menu.addSetting(category,option_container['type'],option,option_container['description'],option_container['values'] if 'values' in option_container else [],option_container['value'])
            config_menu.addSpacer(category)


        config_menu.exec()

class LaunchWorkerObject(QObject):

    fadeout_anim = pyqtSignal()

    def run(self):
        time.sleep(1.5)
        self.fadeout_anim.emit()
        return

class ConfirmDownload(QDialog):
    def __init__(self,message):
        super().__init__()

        self.setWindowTitle("Modpack Install")
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