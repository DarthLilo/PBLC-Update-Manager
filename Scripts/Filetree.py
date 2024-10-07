import os, zipfile, winreg
from .Logging import Logging
from .Util import Util

class Filetree():

    def VerifyFolder(path):
        if os.path.exists(os.path.normcase(path)):
            return True
        
        Filetree.MakeTree(path)
    
    def MakeTree(path):

        os.makedirs(path)
        return
    
    def VerifyList(paths):
        for path in paths:
            Filetree.VerifyFolder(path)
    
    def DecompressZip(zip,destination=None):
        if destination == None:
            destination = os.path.splitext(zip)[0]

        Logging.New(f"Decompressing archive {os.path.basename(zip)}...")
        with zipfile.ZipFile(zip,'a',zipfile.ZIP_DEFLATED) as zipf:
            zipf.extractall(destination)
        os.remove(zip)
        return destination
    
    def LocateLethalCompany():
        custom_lethal_path = ""

        Logging.New("Locating Lethal Company path...")
        steam_install_path = str(Util.ReadReg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\\Wow6432Node\\Valve\\Steam", k = 'InstallPath'))