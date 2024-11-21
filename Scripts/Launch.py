from .Logging import Logging
from .Modpacks import Modpacks
from .Filetree import Filetree
from .Assets import Assets
from .Thunderstore import Thunderstore
import os, subprocess, win10toast
from PyQt6.QtCore import QTimer

class Launch:

    LethalCompanyPath = ""
    SteamFolder = ""
    author = ""
    name = ""
    modpack_path = ""

    def __init__(self, LethalCompanyFolder,SteamFolder):

        Logging.New("Starting launch system...",'startup')

        Launch.LethalCompanyPath = LethalCompanyFolder
        Launch.SteamFolder = SteamFolder

        return
    
    def Setup():
        if not Filetree.VerifyLethalPath(Launch.LethalCompanyPath):
            Logging.New("Error finding Lethal Company path! Please set one manually in config!")
            return False

        if not Filetree.VerifyList([f"{Launch.LethalCompanyPath}/winhttp.dll",f"{Launch.LethalCompanyPath}/doorstop_config.ini",f"{Launch.LethalCompanyPath}/BepInEx/core"],create_folder=False):
            Thunderstore.DownloadBepInEx(Launch.LethalCompanyPath)
        
        return True
    
    def Start(author,name):

        if not Filetree.VerifyLethalPath(Launch.LethalCompanyPath):
            Logging.New("Error finding Lethal Company path! Please set one manually in config!")
            return False

        modpack_path = Modpacks.Path(author,name)
        if not os.path.exists(modpack_path):
            Logging.New("Please select a modpack to launch!",'error')
            return
        
        Launch.author = author
        Launch.name = name
        Launch.modpack_path = modpack_path
        
        Logging.New("Preforming update checks...")
        Modpacks.UpdateVerify(author,name,Launch.actualLaunch)
    
    def actualLaunch():


        Launch.Setup()
        Logging.New(f"Launching modpack {Launch.author}-{Launch.name}")

        launch_command = [
            f"{Launch.SteamFolder}/Steam.exe",
            '-applaunch', '1966720',
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