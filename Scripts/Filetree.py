import os.path
import os, zipfile, winreg, vdf, shutil, subprocess, traceback
from .Logging import Logging
from .Util import Util
from .Config import Config


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
            try:
                zipf.extractall(destination)
            except FileExistsError:
                pass
        try:
            os.remove(zip)
        except PermissionError:
            Logging.New("Zip file is being used by another process, couldn't remove!")
        return destination
    
    def SortFiles(modpack_dir, folder):
        """Distributes files accordingly and returns a list of all of them"""
        
        package_files = []
        bepinex_folder = os.path.join(modpack_dir,"BepInEx")

        for sub_dir in os.listdir(folder):
            sub_dir_path = os.path.join(folder,sub_dir)
            if os.path.isdir(sub_dir_path):
                package_files.extend(Filetree.FileSortAlgorithm(sub_dir,sub_dir_path,folder,bepinex_folder))
        
        for root, dirs, files in os.walk(folder):
            for file in files:
                package_files.append(os.path.relpath(os.path.join(root,file),folder))
        
        return package_files
    
    def FileSortAlgorithm(sub_dir,sub_dir_path,folder,bepinex_folder):
        override_folders = ["patchers","core","config"]
        package_files = []

        if sub_dir in override_folders: #OVERRIDE FOLDER HANDLING
            for root, dirs, files in os.walk(sub_dir_path):
                for file in files:
                    package_files.append(os.path.relpath(os.path.join(root,file),folder))
            shutil.copytree(sub_dir_path,os.path.join(bepinex_folder,sub_dir),dirs_exist_ok=True)
            shutil.rmtree(sub_dir_path)

        elif sub_dir == "plugins": #PLUGINS FOLDER HANDLING
            for filename in os.listdir(sub_dir_path):
                shutil.move(os.path.join(sub_dir_path,filename),folder)
            shutil.rmtree(sub_dir_path)
        
        elif sub_dir == "BepInEx":
            for new_sub_dir in os.listdir(sub_dir_path):
                new_sub_dir_path = os.path.join(sub_dir_path,new_sub_dir)
                package_files.extend(Filetree.FileSortAlgorithm(new_sub_dir,new_sub_dir_path,folder,bepinex_folder))
            shutil.rmtree(sub_dir_path)
        return package_files
    
    def LocateSteam():
        steam_install_path = str(Util.ReadReg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\\Wow6432Node\\Valve\\Steam", k = 'InstallPath')) # Locating 64 bit registry entry

        if steam_install_path == "Check32Bit":
            steam_install_path = str(Util.ReadReg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\\Valve\\Steam", k = 'InstallPath')) # Swapping to 32 bit registry entry

        return steam_install_path

    def LocateLethalCompany():
        custom_lethal_path = Config.Read("general","lethal_company_path","value")
        if os.path.exists(custom_lethal_path):
            return custom_lethal_path

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
    
    def VerifyLethalPath(path):
        Logging.New("Verifying Lethal Company path...")
        return os.path.exists(path)
    
    def IsProcessRunning(process_name):
        Logging.New(f"Checking for {process_name}")
        cmd = 'tasklist /fi "imagename eq {}"'.format(process_name)
        try:
            output = subprocess.check_output(cmd, shell=True).decode('utf-8')
            if process_name.lower() in output.lower():
                return True
            else:
                return False
        except Exception as e:
            Logging.New(traceback.format_exc(), 'error')
            return False
    
    def IsLethalRunning(popup_window):
        if Filetree.IsProcessRunning("Lethal Company.exe"):
            dlg = popup_window()
            result = dlg.exec()
            return True
        return False
    
    def IsPythonInstalled():
        try:
            result = subprocess.run(['python','--version'],capture_output=True,text=True)
            if result.returncode == 0:
                Logging.New(f"Python is installed running version {result.stdout.strip()}")
                return True
            else:
                Logging.New("Python is not installed",'error')
                return False
        except FileNotFoundError:
            Logging.New("Python is not installed",'error')
            return False