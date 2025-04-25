from .Logging import Logging
from .Networking import Networking
from .Filetree import Filetree
from .Maths import Maths
from .Game import Game
import requests, pickle, json, os, shutil, threading

from PyQt6.QtCore import QObject, pyqtSignal

class Cache():

    PackageIndex = ""
    PackageCache = ""
    CacheFolder = ""
    ModCache = ""
    Packages = {}
    SelectedModpack = ""
    LoadedMods = {}
    StartCache = False

    def __init__(self,CacheFolder):

        Logging.New("Starting caching system...",'startup')
        Cache.CacheFolder = CacheFolder

        return
    
    def SetupCache():
        Cache.PackageIndex = os.path.join(Cache.CacheFolder,Game.package_index)
        Cache.PackageCache = os.path.join(Cache.CacheFolder,Game.package_cache)
        Cache.ModCache = os.path.join(Cache.CacheFolder,"ModCache",Game.game_id)

        if not os.path.exists(Cache.ModCache):
            os.makedirs(Cache.ModCache,exist_ok=True)
        
        if not os.path.exists(Cache.PackageIndex) or not os.path.exists(Cache.PackageCache):
            Cache.StartCache = True
        else:
            Cache.Packages = Cache.LoadIndex()

    
    def Download(cache_status_func=None):
        """Downloads the latest cache file from the Thunderstore CDN"""
        Logging.New("Downloading the latest cache")

        Networking.DownloadFromUrl(f"https://thunderstore.io/c/{Game.ts_url_prefix}/api/v1/package/",f"{Cache.CacheFolder}/{Game.package_index}",cache_status_func)
    
    def Index(cache_status_func=None):
        """Indexes the cache file into memory, packages can be retrieved using the [author] [name] format"""
        Logging.New("Beginning package index process, this might take a while...")
        if callable(cache_status_func): cache_status_func(f"Caching mods...")
        Cache.Packages.clear()
        if os.path.exists(Cache.PackageIndex):
            with open(Cache.PackageIndex, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for entry in data:
                    key = (entry['owner'], entry['name'])
                    Cache.Packages[key] = entry
                Logging.New("Finished Caching")
        
        Cache.StartCache = False
        return
    
    def SaveIndex():
        """Saves the current memory index into a file"""
        with open(Cache.PackageCache, 'wb') as file:
            pickle.dump(Cache.Packages, file)
        Logging.New("Saved package index to pk1 file")
    
    def LoadIndex():
        """Loads the previous index into memory"""
        with open(Cache.PackageCache, 'rb') as file:
            return pickle.load(file)
        
        Logging.New("Load package index from pk1 file")
        
        return {}
    
    def Reset():
        Cache.Packages.clear()
        try:
            os.remove(Cache.PackageIndex)
            os.remove(Cache.PackageCache)
        except FileNotFoundError:
            Logging.New("Cache reset file not found!",'error')
    
    def Update(import_func=None,cache_status_func=None):

        Cache.StartWorkerObject(import_func,cache_status_func)
    
    def StartWorkerObject(import_func,cache_status_func):
        worker_object = CacheWorkerObject()

        worker_object.update_status.connect(cache_status_func)
        if callable(import_func): worker_object.finished.connect(import_func)
        
        working_thread = threading.Thread(target=worker_object.run,daemon=True)
        working_thread.start()

    def Get(owner,name,version="",full_package=False):
        """Gets the matching package entry for the owner and name specified, if a version is specified it will return the entry for that version"""
        key = (owner, name)

        if version.strip():
            try:
                packages = Cache.Packages.get(key)['versions']
            except TypeError:
                return {}
            
            for package in packages:
                if package['version_number'] == version:
                    return package
                
            Logging.New(f"No matching version found: [{owner}-{name}-{version}]",'warning')

            return {}
        
        if full_package:
            return Cache.Packages.get(key)
        
        return Cache.Packages.get(key)['versions'][0]

    def Exists():
        return os.path.exists(Cache.PackageIndex)

    class FileCache():

        def IsCached(author,name,mod_version):
            return os.path.exists(f"{Cache.ModCache}/{author}-{name}-{mod_version}.zip")
        
        def Get(author,name,mod_version):
            return f"{Cache.ModCache}/{author}-{name}-{mod_version}.zip"
        
        def AddMod(path):
            try:
                file_name = os.path.basename(path)
                new_loc = f"{Cache.ModCache}/{file_name}"

                if os.path.exists(new_loc):
                    os.remove(new_loc)
                    Logging.New(f"Cleared old cache for {file_name}")

                shutil.copy(path,new_loc)

                Logging.New(f"Cached file {file_name}")
            except FileNotFoundError:
                pass

            return
        
        def DeleteMod(author,name,mod_version):
            if Cache.FileCache.IsCached(author,name,mod_version):
                os.remove(f"{Cache.ModCache}/{author}-{name}-{mod_version}.zip")
                Logging.New(f"Deleted {author}-{name}-{mod_version} from cache!")
        
        def Clear():
            for folder in os.listdir(Cache.ModCache):
                os.remove(f"{Cache.ModCache}/{folder}")
            Logging.New("Cleared Mod Cache!")

class CacheWorkerObject(QObject):

    update_status = pyqtSignal(str)
    finished = pyqtSignal()

    def run(self):
        Cache.Reset()
        Cache.Download(self.update_status.emit)
        Cache.Index(self.update_status.emit)
        Cache.SaveIndex()
        self.finished.emit()