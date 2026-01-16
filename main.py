import sys, os, json, time, random

from PyQt6.QtCore import QSize, Qt, pyqtProperty, QLoggingCategory
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSizePolicy, QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QMovie, QAction, QIcon, QFontDatabase
import Scripts, subprocess

############################### Variables ###############################

if getattr(sys,'frozen',False):
    CurFolder = os.path.dirname(sys.executable)
else:
    CurFolder = os.path.dirname(__file__)


ReleaseTag = "Stable"
PBLCVersion = "1.2.1"
ProgramDataFolder = os.path.normpath(f"{CurFolder}/ProgramData")
LoggingFolder = os.path.normpath(f"{ProgramDataFolder}/Logs")
ModpacksFolder = os.path.normpath(f"{ProgramDataFolder}/Modpacks")
CacheFolder = os.path.normpath(f"{ProgramDataFolder}/Cache")
AssetsFolder = os.path.normpath(f"{CurFolder}/ProgramAssets")
GamesFolder = os.path.normpath(f"{AssetsFolder}/games")


############################### Verify Folders ##########################


Scripts.Filetree.VerifyList([ProgramDataFolder,LoggingFolder,ModpacksFolder,CacheFolder,AssetsFolder])


############################### Start Subsystems ########################
Scripts.Logging(LoggingFolder,PBLCVersion)
Scripts.Config(ProgramDataFolder)

Scripts.Registry.EnsureProtocolHandler()

if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = None

server = Scripts.ProtocolHandler.send_url_to_instance(url)
if not server:
    Scripts.Logging.New("App already running, closing!")
    sys.exit()

Scripts.Assets(AssetsFolder)
Scripts.QueueMan()
Scripts.Cache(CacheFolder)
Scripts.Modpacks(ModpacksFolder)
Scripts.Launch(Scripts.Filetree.LocateSteam())
Scripts.Networking.PBLCVersion = PBLCVersion
Scripts.Networking.CurFolder = CurFolder
Scripts.Game(GamesFolder)

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
                return
            sys.exit()

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


        self.main_menu = Scripts.UI.GameSelectionMenu(self.triggerMainMenu)
        for game in Scripts.Game.data_library:
            game_data = Scripts.Game.data_library[game]
            self.main_menu.addGame(Scripts.Assets.getGameCover(game),game_data['name'],game_data['developer'],game)
        pblc_layout.addWidget(self.main_menu)

        layout_container = QWidget()
        layout_container.setLayout(pblc_layout)

        self.setCentralWidget(layout_container)
    
    def triggerMainMenu(self):
        
        self.main_menu = Scripts.UI(self.backToGameSelection)
        self.setCentralWidget(self.main_menu)
    
    def backToGameSelection(self):
        self.main_menu = Scripts.UI.GameSelectionMenu(self.triggerMainMenu)
        for game in Scripts.Game.data_library:
            game_data = Scripts.Game.data_library[game]
            self.main_menu.addGame(Scripts.Assets.getGameCover(game),game_data['name'],game_data['developer'],game)
        Scripts.Game.game_id = None


        self.setCentralWidget(self.main_menu)

    
    def OpenConfigScreen(self):
        config_menu = Scripts.UIElements.ConfigMenu()

        config_data = Scripts.Config.Get()

        for category in config_data:
            config_menu.addCategory(category)

            for option in config_data[category]:
                option_container = config_data[category][option]
                config_menu.addSetting(category,option_container['type'],option,option_container['description'],option_container['values'] if 'values' in option_container else [],option_container['value'])
            config_menu.addSpacer(category)


        config_menu.exec()

    def closeEvent(self, event):
        if Scripts.Config.Read("general","major_task_running",'value') == False or Scripts.Config.Read("general","major_task_running",'value') == "False":
            event.accept()
        else:
            event.ignore()
    
    def DownloadCache(self):
        if Scripts.Game.game_id == None:
            self.NoGameSelected()
            return
        self.main_menu.ShowLoadingScreenCacheUpdate()
        Scripts.Cache.Update(self.main_menu.ShowModpackSelectionScreen,cache_status_func=self.main_menu._screen_loading_cache_update.setStatus)
    
    def ClearCache(self):
        if Scripts.Game.game_id == None:
            self.NoGameSelected()
            return
        Scripts.Cache.FileCache.Clear()

    def CheckForUpdates(self):
        Scripts.Networking.CheckForUpdatesManager()

    def OpenConfig(self):
        self.OpenConfigScreen()
    
    def NoGameSelected(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("Please select a game first before using the cache!")
        msg.setWindowTitle("No Game Selected")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setWindowIcon(QIcon(Scripts.Assets.getResource(Scripts.Assets.ResourceTypes.app_icon)))

        result = msg.exec()

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
app.setStyle('Fusion')
window = PBLCWindow()
window.show()

app.exec()

Scripts.Logging.Close()