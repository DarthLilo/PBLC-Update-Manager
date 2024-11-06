import sys, os, json, time, random

from PyQt6.QtCore import QSize, Qt, pyqtProperty, QLoggingCategory
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase
import Scripts

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

class PBLCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PBLC Update Manager - [{ReleaseTag} - {PBLCVersion}]")
        self.setMinimumSize(1000,580)
        self.setWindowIcon(QIcon(Scripts.Assets.getResource(Scripts.Assets.ResourceTypes.app_icon)))

        ### LOAD MENU BAR
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")

        download_cache = QAction("Download Cache",self)
        download_cache.triggered.connect(self.DownloadCache)
        file_menu.addAction(download_cache)

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
    
    def DownloadCache(self):
        self.main_menu.ShowLoadingScreenCacheUpdate()
        Scripts.Cache.Update(self.main_menu.ShowModpackSelectionScreen,cache_status_func=self.main_menu._screen_loading_cache_update.setStatus)

    def CheckForUpdates(self):
        Scripts.Networking.CheckForUpdatesManager()

    def OpenConfig(self):
        self.main_menu.OpenConfigScreen()

# ACTUALLY START THE WINDOW

app = QApplication(sys.argv)
window = PBLCWindow()
window.show()

app.exec()

Scripts.Logging.Close()