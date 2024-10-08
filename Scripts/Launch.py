from .Logging import Logging
from .Modpacks import Modpacks
from .Filetree import Filetree
from .Thunderstore import Thunderstore
import os, shutil, subprocess

class Launch:

    LethalCompanyPath = ""
    SteamFolder = ""

    def __init__(self, LethalCompanyFolder,SteamFolder):

        Logging.New("Starting launch system...",'startup')

        Launch.LethalCompanyPath = LethalCompanyFolder
        Launch.SteamFolder = SteamFolder

        return
    
    def Setup():

        if not Filetree.VerifyList([f"{Launch.LethalCompanyPath}/winhttp.dll",f"{Launch.LethalCompanyPath}/doorstop_config.ini",f"{Launch.LethalCompanyPath}/BepInEx/core"],create_folder=False):
            Thunderstore.DownloadBepInEx(Launch.LethalCompanyPath)
    
    def Start(author,name):

        modpack_path = Modpacks.Path(author,name)
        if not os.path.exists(modpack_path):
            Logging.New("Please select a modpack to launch!",'error')
            return
        Launch.Setup()
        Logging.New(f"Launching modpack {author}-{name}")

        launch_command = [
            f"{Launch.SteamFolder}/Steam.exe",
            '-applaunch', '1966720',
            '--doorstop-enable', 'true',
            '--doorstop-target', f"{modpack_path}/BepInEx/core/BepInEx.Preloader.dll"
        ]

        subprocess.Popen(launch_command,shell=True)

        return