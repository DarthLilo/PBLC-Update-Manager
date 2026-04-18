from .Logging import Logging
from .Modpacks import Modpacks
from .Filetree import Filetree
from .Assets import Assets
from .Thunderstore import Thunderstore
from .Game import Game
from .Config import Config
import os, subprocess, win11toast, threading, traceback
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox

class Launch:

    GamePath = ""
    SteamFolder = ""
    author = ""
    name = ""
    modpack_path = ""

    def __init__(self, SteamFolder):

        Logging.New("Starting launch system...",'startup')

        Launch.SteamFolder = SteamFolder
        

        return
    
    def SetStartupGame():
        Launch.GamePath = Filetree.LocateGame(Game.game_id,Game.config_value,Game.steam_id)

    
    def Setup():
        if not Filetree.VerifyGamePath(Launch.GamePath):
            Logging.New(f"Error finding {Game.game_id} path! Please set one manually in config!",'warning')
            return False

        if not Filetree.VerifyList([
            f"{Launch.GamePath}/winhttp.dll",
            f"{Launch.GamePath}/doorstop_config.ini",
            f"{Launch.GamePath}/BepInEx/core"
            
            ],create_folder=False):
            Logging.New("Attempting repair on BepInEx install for base game")
            Thunderstore.DownloadBepInEx(Launch.GamePath)
        
        if not Filetree.VerifyList([
            f"{Launch.modpack_path}/winhttp.dll",
            f"{Launch.modpack_path}/doorstop_config.ini",
            f"{Launch.modpack_path}/BepInEx/core"
            
            ],create_folder=False):
            Logging.New("Attempting repair on BepInEx install for modpack")
            Thunderstore.DownloadBepInEx(Launch.modpack_path)
        
        return True
    
    def Start(author,name,extra=False):

        if not Filetree.VerifyGamePath(Launch.GamePath):
            Logging.New(f"Error finding {Game.game_id} path! Please set one manually in config!",'warning')
            return False

        modpack_path = Modpacks.Path(author,name)
        if not os.path.exists(modpack_path):
            Logging.New("Please select a modpack to launch!",'warning')
            return
        
        Launch.author = author
        Launch.name = name
        Launch.modpack_path = modpack_path
        
        skip_launch_update = Config.Read("debug","skip_update_check_on_launch","value")

        print(f"actual value {skip_launch_update}")

        if skip_launch_update == "True":
            Logging.New("Skipping update checker.")
            Launch.actualLaunch(extra)
        else:
            Logging.New("Preforming update checks...")
            Modpacks.UpdateVerify(author,name,lambda: Launch.actualLaunch(extra)) 
        
    
    def actualLaunch(extra=False):


        Launch.Setup()
        Logging.New(f"Launching modpack {Launch.author}-{Launch.name}")

        launch_command = [
            f"{Launch.SteamFolder}/Steam.exe",
            '-applaunch', Game.steam_id,
            '--doorstop-enable', 'true',
            '--doorstop-target', os.path.normpath(f"{Launch.modpack_path}/BepInEx/core/BepInEx.Preloader.dll"),
            '--doorstop-enabled', 'true',
            '--doorstop-target-assembly', os.path.normpath(f"{Launch.modpack_path}/BepInEx/core/BepInEx.Preloader.dll")
        ]

        if extra:
            launch_command = [
                f"{Launch.GamePath}/{Game.game_id}.exe",
                # BepinEx V3
                '--doorstop-enable', 'true',
                '--doorstop-target', os.path.normpath(f"{Launch.modpack_path}/BepInEx/core/BepInEx.Preloader.dll"),
                # BepinEx V4
                '--doorstop-enabled', 'true',
                '--doorstop-target-assembly', os.path.normpath(f"{Launch.modpack_path}/BepInEx/core/BepInEx.Preloader.dll")
            ]
        
        Logging.New(f"Starting Lethal Company using launch command:\n{launch_command}",'info')
        try:
            subprocess.Popen(launch_command,shell=True)
            QTimer.singleShot(0, Launch.triggerNotif)

        except Exception as e:
            Logging.New(f"Uh oh, Critical error when launching the game!")
            Logging.New(traceback.format_exc(),'error')

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("An unknown issue has occured when starting the game, please see the log for details!")
            msg.setWindowTitle("Error when starting the game!")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))

        
        
        
        return True
    
    def triggerNotif():
        threading.Thread(target=Launch.ShowNotif,daemon=True).start()

    def ShowNotif():

        launch_hero = {
            'src': Assets.getResource(Assets.ResourceTypes.launch_hero),
            'placement': 'hero'
        }

        win11toast.toast(
            "Starting Modpack!",
            f'Starting [{Launch.author}-{Launch.name}]!',
            icon=Assets.getResource(Assets.ResourceTypes.app_icon),
            image=launch_hero,
            audio='ms-winsoundevent:Notification.Reminder'
        )