import sys, os, json, time, random

from PyQt6.QtCore import QSize, Qt, pyqtProperty
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase
import Scripts
import Scripts.Assets

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
LethalCompanyFolder = Scripts.Filetree.LocateLethalCompany()
Scripts.Cache(CacheFolder)
Scripts.Modpacks(ModpacksFolder)
Scripts.Launch(LethalCompanyFolder,Scripts.Filetree.LocateSteam())

#########################################################################

#Scripts.Modpacks.Import("E:\\Lilos Coding\\PBML\\ProgramData\\DarthLilo-teehee.json")


#Scripts.Modpacks.Setup(Scripts.Util.OpenJson("E:\\Lilos Coding\\PBML\\ProgramData\\DarthLilo-teehee.json"))

#Scripts.Modpacks.New("DarthLilo","teehee")
#Scripts.Modpacks.Select("DarthLilo","teehee")

#time.sleep(60)

#Scripts.Launch.Start("DarthLilo","teehee")

#Scripts.Modpacks.Export("DarthLilo","teehee")

class PBLCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PBLC Update Manager - [VERSION HERE]")
        self.setMinimumSize(1000,580)
        self.setWindowIcon(QIcon("E:\\Lilos Coding\\PBML\\assets\\pill_bottle.ico"))

        ### LOAD MENU BAR
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        modpacks_menu = menu.addMenu("&Modpacks")
        view_menu = menu.addMenu("&View")

        dev_action = QAction("dev action",self)
        dev_action.triggered.connect(self.devAction)
        file_menu.addAction(dev_action)

        pblc_layout = QGridLayout()
        #pblc_layout.setSpacing(16)  
        self.main_menu = Scripts.UI(AssetsFolder)
        
        pblc_layout.addWidget(self.main_menu)

        layout_container = QWidget()
        layout_container.setLayout(pblc_layout)

        self.setCentralWidget(layout_container)
    
    def devAction(self):
        self.main_menu.FadeToModpackSelection(self.main_menu._screen_loading)


# ACTUALLY START THE WINDOW

#app = QApplication(sys.argv)
#window = PBLCWindow()
#window.show()

#app.exec()

Scripts.Logging.Close()