import sys, os, json, time

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
Scripts.Launch(LethalCompanyFolder,Scripts.Filetree.LocateSteam())

#########################################################################

Scripts.Modpacks.New("DarthLilo","teehee")
Scripts.Modpacks.Select("DarthLilo","teehee")
#Scripts.Modpacks.Mods.Add(author="IAmBatby",mod="LethalLevelLoader",mod_version="1.3.10")
#Scripts.Modpacks.Mods.Add("https://thunderstore.io/c/lethal-company/p/x753/More_Suits/1.3.3")
#Scripts.Modpacks.Mods.Add("https://thunderstore.io/c/lethal-company/p/ManiaBania/1000_Quota_Stare/")

#Scripts.Modpacks.DeleteMod("x753","More_Suits","1.4.3")
#Scripts.Logging.New(Scripts.Modpacks.Mods.CheckForUpdates("x753","More_Suits"))
#Scripts.Modpacks.Mods.Update("x753","More_Suits")
#Scripts.Modpacks.Mods.Delete("x753","More_Suits")
#Scripts.Modpacks.Delete("DarthLilo","teehee")

#Scripts.Modpacks.Mods.Toggle("x753","More_Suits")

#Scripts.Modpacks.ScanForUpdates()

Scripts.QueueMan.Debug()

time.sleep(15)

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