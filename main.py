import sys, os, json, time, random

from PyQt6.QtCore import QSize, Qt, pyqtProperty, QLoggingCategory
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QDialog, QDialogButtonBox, QLabel, QVBoxLayout
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase
import Scripts, subprocess

############################### Variables ###############################

if getattr(sys,'frozen',False):
    CurFolder = os.path.dirname(sys.executable)
else:
    CurFolder = os.path.dirname(__file__)


ReleaseTag = "Alpha"
PBLCVersion = "1.0.0"
ProgramDataFolder = os.path.normpath(f"{CurFolder}/ProgramData")
LoggingFolder = os.path.normpath(f"{ProgramDataFolder}/Logs")
ModpacksFolder = os.path.normpath(f"{ProgramDataFolder}/Modpacks")
CacheFolder = os.path.normpath(f"{ProgramDataFolder}/Cache")
AssetsFolder = os.path.normpath(f"{CurFolder}/ProgramAssets")
LethalCompanyFolder = ""


############################### Verify Folders ##########################


Scripts.Filetree.VerifyList([ProgramDataFolder,LoggingFolder,ModpacksFolder,CacheFolder,AssetsFolder])


############################### Start Subsystems ########################


Scripts.Logging(LoggingFolder,PBLCVersion)
Scripts.Assets(AssetsFolder)
Scripts.Config(ProgramDataFolder)
Scripts.QueueMan()
LethalCompanyFolder = Scripts.Filetree.LocateLethalCompany()
Scripts.Cache(CacheFolder)
Scripts.Modpacks(ModpacksFolder)
Scripts.Launch(LethalCompanyFolder,Scripts.Filetree.LocateSteam())
Scripts.Networking.PBLCVersion = PBLCVersion
Scripts.Networking.CurFolder = CurFolder

#########################################################################

Scripts.Config.Write("general","major_task_running",False)

class PBLCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PBLC Update Manager - [{ReleaseTag} - {PBLCVersion}]")
        self.setMinimumSize(1000,580)
        self.setWindowIcon(QIcon(Scripts.Assets.getResource(Scripts.Assets.ResourceTypes.app_icon)))
        
        if not Scripts.Filetree.IsPythonInstalled():
            Scripts.Logging.New("Python isn't installed, prompting user to install")
            dlg = PythonInstalled()
            response = dlg.exec()
            if response:
                subprocess.Popen(f"{CurFolder}/lib/python_install.bat")
            else:
                sys.exit()
                return

        ### LOAD MENU BAR
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        cache_menu = menu.addMenu("&Cache")

        download_cache = QAction("Download Cache",self)
        download_cache.triggered.connect(self.DownloadCache)
        cache_menu.addAction(download_cache)

        reset_cache = QAction("Clear Cache",self)
        reset_cache.triggered.connect(self.ClearCache)
        cache_menu.addAction(reset_cache)

        update_button = QAction("Check For Updates",self)
        update_button.triggered.connect(self.CheckForUpdates)
        file_menu.addAction(update_button)

        config_menu  =QAction("Preferences",self)
        config_menu.triggered.connect(self.OpenConfig)
        file_menu.addAction(config_menu)

        #Start UI
        pblc_layout = QGridLayout()
        self.main_menu = Scripts.UI()
        
        pblc_layout.addWidget(self.main_menu)

        layout_container = QWidget()
        layout_container.setLayout(pblc_layout)

        self.setCentralWidget(layout_container)
    
    def closeEvent(self, event):
        if Scripts.Config.Read("general","major_task_running",'value') == False or Scripts.Config.Read("general","major_task_running",'value') == "False":
            event.accept()
        else:
            event.ignore()
    
    def DownloadCache(self):
        self.main_menu.ShowLoadingScreenCacheUpdate()
        Scripts.Cache.Update(self.main_menu.ShowModpackSelectionScreen,cache_status_func=self.main_menu._screen_loading_cache_update.setStatus)
    
    def ClearCache(self):
        Scripts.Cache.FileCache.Clear()

    def CheckForUpdates(self):
        Scripts.Networking.CheckForUpdatesManager()

    def OpenConfig(self):
        self.main_menu.OpenConfigScreen()

class PythonInstalled(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Launcher Update")
        self.setWindowIcon(QIcon(Scripts.Assets.getResource(Scripts.Assets.ResourceTypes.app_icon)))

        Buttons = (
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        self.button_box = QDialogButtonBox(Buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        self.message = QLabel("Python isn't installed, please install it before you can continue!")
        layout.addWidget(self.message)
        layout.addWidget(self.button_box)

# ACTUALLY START THE WINDOW

app = QApplication(sys.argv)
window = PBLCWindow()
window.show()

app.exec()

Scripts.Logging.Close()