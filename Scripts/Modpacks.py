from .Logging import Logging
from .Time import Time
from .Thunderstore import Thunderstore
from .Cache import Cache
import os, json, shutil

class Modpacks:

    ModpackFolder = ""
    def __init__(self, ModpacksFolder):
        Logging.New("Starting modpack engine...")
        Modpacks.ModpackFolder = ModpacksFolder
        return
    
    def New(author,name):
        
        modpack_location = f"{Modpacks.ModpackFolder}/{author}-{name}"
        
        if os.path.exists(modpack_location):
            Logging.New("A modpack with this name exists already!",'warning')
            return ""
        
        os.mkdir(modpack_location)
        Modpacks.CreateJson(author,name,modpack_location)
        Thunderstore.DownloadBepInEx(modpack_location)

        return
    
    def CreateJson(author,name,modpack_location):
        modpack_metadata = {
            "author": author,
            "name": name,
            "version": "1.0.0",
            "update_date": Time.CurrentDate()
        }

        with open(f"{modpack_location}/modpack.json",'w') as modpack_json:
            modpack_json.write(json.dumps(modpack_metadata,indent=4))


        return
    
    def Select(author,name):
        Cache.SelectedModpack = f"{Modpacks.ModpackFolder}/{author}-{name}"
        Logging.New(f"Selected modpack {author}-{name}!")
    
    def Delete(author,name):

        target_modpack = f"{Modpacks.ModpackFolder}/{author}-{name}"
        if os.path.exists(target_modpack):
            shutil.rmtree(target_modpack)
        return