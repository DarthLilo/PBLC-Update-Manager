import os, zipfile, winreg, vdf
from .Logging import Logging
from .Util import Util

class Filetree():

    def VerifyFolder(path,create_folder=True):
        if os.path.exists(os.path.normcase(path)):
            return True
        
        if create_folder:
            Filetree.MakeTree(path)
        
        return False
    
    def MakeTree(path):

        os.makedirs(path)
        return
    
    def VerifyList(paths, create_folder=True):
        for path in paths:
            file = Filetree.VerifyFolder(path, create_folder)
            if not create_folder and not file:
                return False
        
        return True
    
    def DecompressZip(zip,destination=None):
        """Decompresses a zip file and returns a path"""
        if destination == None:
            destination = os.path.splitext(zip)[0]

        Logging.New(f"Decompressing archive {os.path.basename(zip)}...")
        with zipfile.ZipFile(zip,'a',zipfile.ZIP_DEFLATED) as zipf:
            zipf.extractall(destination)
        os.remove(zip)
        return destination
    
    def GetFiles(path):
        for folder, _, files in os.walk(path):
            for file in files:
                absolute_path = os.path.join(folder,file)
                relative_path = os.path.relpath(absolute_path,os.path.dirname(path))
                Logging.New(relative_path)

    def LocateLethalCompany():
        custom_lethal_path = ""

        Logging.New("Locating Lethal Company path...")
        steam_install_path = str(Util.ReadReg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\\Wow6432Node\\Valve\\Steam", k = 'InstallPath')) # Locating 64 bit registry entry

        if steam_install_path == "Check32Bit":
            steam_install_path = str(Util.ReadReg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\\Valve\\Steam", k = 'InstallPath')) # Swapping to 32 bit registry entry

        steamapps = steam_install_path+"\\steamapps"
        library_folders = steamapps+"\\libraryfolders.vdf"
        libdata = vdf.load(open(library_folders))
        lethal_company_steamid = "1966720"

        for library in libdata['libraryfolders']:
            cur_lib = libdata['libraryfolders'][library]
            apps = cur_lib["apps"]
            if lethal_company_steamid in apps:
                lethal_path = os.path.normpath(f"{cur_lib['path']}/steamapps/common/Lethal Company")
                Logging.New(f"Located Lethal Company path: {lethal_path}")
                return lethal_path