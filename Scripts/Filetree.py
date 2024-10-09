import os.path
import os, zipfile, winreg, vdf, shutil
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
    
    def SortFiles(modpack_dir,folder):

        package_files = []
        special_folders = ["plugins","patchers","core","config"]

        for root, dirs, files in os.walk(folder):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root,file),folder)
                package_files.append(rel_path)
        
        for sub_dir in os.listdir(folder):
            if os.path.isdir(f"{folder}/{sub_dir}"):
                if sub_dir == "BepInEx":
                    shutil.copytree(f"{folder}/{sub_dir}",f"{modpack_dir}/BepInEx",dirs_exist_ok=True)
                    shutil.rmtree(f"{folder}/{sub_dir}")
                    continue
                for tag in special_folders:
                    if sub_dir == tag:
                        shutil.copytree(f"{folder}/{sub_dir}",f"{modpack_dir}/BepInEx/{tag}",dirs_exist_ok=True)
                        shutil.rmtree(f"{folder}/{sub_dir}")
                        break
        
        return package_files
    
    def LocateSteam():
        steam_install_path = str(Util.ReadReg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\\Wow6432Node\\Valve\\Steam", k = 'InstallPath')) # Locating 64 bit registry entry

        if steam_install_path == "Check32Bit":
            steam_install_path = str(Util.ReadReg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\\Valve\\Steam", k = 'InstallPath')) # Swapping to 32 bit registry entry

        return steam_install_path

    def LocateLethalCompany():
        custom_lethal_path = ""

        Logging.New("Locating Lethal Company path...")

        steamapps = Filetree.LocateSteam()+"\\steamapps"
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
    
    def DirSize(target_path):
        total_size = 0
        for path, dirs, files in os.walk(target_path):
            for f in files:
                filepath = os.path.join(path,f)
                total_size += os.path.getsize(filepath)
        return total_size