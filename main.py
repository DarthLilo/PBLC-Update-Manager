import sys, os, json

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
import Scripts

############################### Variables ###############################

CurFolder = os.path.dirname(__file__)

ProgramDataFolder = os.path.normpath(f"{CurFolder}/ProgramData")
LoggingFolder = os.path.normpath(f"{ProgramDataFolder}/Logs")
ModpacksFolder = os.path.normpath(f"{ProgramDataFolder}/Modpacks")
CacheFolder = os.path.normpath(f"{ProgramDataFolder}/Cache")
LethalCompanyFolder = ""


############################### Verify Folders ##########################


Scripts.Filetree.VerifyList([ProgramDataFolder,LoggingFolder,ModpacksFolder,CacheFolder])


############################### Start Subsystems ########################


Scripts.Logging(LoggingFolder)
Scripts.Config(ProgramDataFolder)
LethalCompanyFolder = Scripts.Filetree.LocateLethalCompany()
Scripts.Cache(CacheFolder)
Scripts.Modpacks(ModpacksFolder)
Scripts.Launch(LethalCompanyFolder)

#########################################################################

Scripts.Modpacks.New("DarthLilo","teehee")
Scripts.Modpacks.Select("DarthLilo","teehee")
#Scripts.Thunderstore.Download("https://thunderstore.io/c/lethal-company/p/DarthLilo/MagnetLock/")
#Scripts.Thunderstore.Download("https://thunderstore.io/c/lethal-company/p/AinaVT/LethalConfig/")
#Scripts.Thunderstore.Download("https://thunderstore.io/c/lethal-company/p/DarthLilo/ItemWeights/")
Scripts.Thunderstore.Download("https://thunderstore.io/c/lethal-company/p/Rune580/LethalCompany_InputUtils/")

#Scripts.Launch.Start("DarthLilo","teehee")

class PBLCWindowLaunch(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PBLC Update Manager")

        button = QPushButton("Press Me!")

        self.setFixedSize(QSize(400,300))
        self.setCentralWidget(button)


#mod, author, mod_version = Scripts.Networking.Extract("https://thunderstore.io/c/lethal-company/p/DarthLilo/MagnetLock/1.2.0")
#
#Scripts.Networking.DownloadPackage(mod,author,mod_version)

# ACTUALLY START THE WINDOW

#app = QApplication(sys.argv)
#window = PBLCWindowLaunch()
#window.show()
#
#app.exec()

Scripts.Logging.Close()