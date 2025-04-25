from .Logging import Logging
from .Modpacks import Modpacks
from .Filetree import Filetree
from .Assets import Assets
from .Thunderstore import Thunderstore
from .Game import Game
import os, subprocess, win10toast
from PyQt6.QtCore import QTimer

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
            Logging.New(f"Error finding {Game.game_id} path! Please set one manually in config!")
            return False

        if not Filetree.VerifyList([f"{Launch.GamePath}/winhttp.dll",f"{Launch.GamePath}/doorstop_config.ini",f"{Launch.GamePath}/BepInEx/core"],create_folder=False):
            Thunderstore.DownloadBepInEx(Launch.GamePath)
        
        return True
    
    def Start(author,name,extra=False):

        if not Filetree.VerifyGamePath(Launch.GamePath):
            Logging.New(f"Error finding {Game.game_id} path! Please set one manually in config!")
            return False

        modpack_path = Modpacks.Path(author,name)
        if not os.path.exists(modpack_path):
            Logging.New("Please select a modpack to launch!",'error')
            return
        
        Launch.author = author
        Launch.name = name
        Launch.modpack_path = modpack_path
        
        Logging.New("Preforming update checks...")
        Modpacks.UpdateVerify(author,name,lambda: Launch.actualLaunch(extra))
    
    def actualLaunch(extra=False):


        Launch.Setup()
        Logging.New(f"Launching modpack {Launch.author}-{Launch.name}")

        launch_command = [
            f"{Launch.SteamFolder}/Steam.exe",
            '-applaunch', Game.steam_id,
            '--doorstop-enable', 'true',
            '--doorstop-target', f"{Launch.modpack_path}/BepInEx/core/BepInEx.Preloader.dll"
        ]

        if extra:
            launch_command = [
                f"{Launch.GamePath}/{Game.game_id}.exe",
                '--doorstop-enable', 'true',
                '--doorstop-target', f"{Launch.modpack_path}/BepInEx/core/BepInEx.Preloader.dll"
            ]
        
        subprocess.Popen(launch_command,shell=True)

        QTimer.singleShot(0, Launch.ShowNotif)
        
        
        return True
    
    def ShowNotif():
        notif = win10toast.ToastNotifier()
        notif.show_toast(
            "Starting Modpack!",f'Starting [{Launch.author}-{Launch.name}]!',Assets.getResource(Assets.ResourceTypes.app_icon),threaded=True
        )