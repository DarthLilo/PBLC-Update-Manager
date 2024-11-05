import sys, os, json, time, random

from PyQt6.QtCore import QSize, Qt, pyqtProperty, QLoggingCategory
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase
import Scripts

############################### Variables ###############################

CurFolder = os.path.dirname(__file__)

ProgramDataFolder = os.path.normpath(f"{CurFolder}/ProgramData")
LoggingFolder = os.path.normpath(f"{ProgramDataFolder}/Logs")
ModpacksFolder = os.path.normpath(f"{ProgramDataFolder}/Modpacks")
CacheFolder = os.path.normpath(f"{ProgramDataFolder}/Cache")
AssetsFolder = os.path.normpath(f"{CurFolder}/ProgramAssets")
LethalCompanyFolder = ""


############################### Verify Folders ##########################


Scripts.Filetree.VerifyList([ProgramDataFolder,LoggingFolder,ModpacksFolder,CacheFolder,AssetsFolder])


############################### Start Subsystems ########################


Scripts.Logging(LoggingFolder)
Scripts.Assets(AssetsFolder)
Scripts.Config(ProgramDataFolder)
Scripts.QueueMan()
LethalCompanyFolder = Scripts.Filetree.LocateLethalCompany()
Scripts.Cache(CacheFolder)
Scripts.Modpacks(ModpacksFolder)
Scripts.Launch(LethalCompanyFolder,Scripts.Filetree.LocateSteam())

#########################################################################

class PBLCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PBLC Update Manager - [VERSION HERE]")
        self.setMinimumSize(1000,580)
        self.setWindowIcon(QIcon(Scripts.Assets.getResource(Scripts.Assets.ResourceTypes.app_icon)))

        ### LOAD MENU BAR
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")

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

        
    
    def OpenConfig(self):
        self.main_menu.OpenConfigScreen()


# ACTUALLY START THE WINDOW

app = QApplication(sys.argv)
window = PBLCWindow()
window.show()

app.exec()

Scripts.Logging.Close()