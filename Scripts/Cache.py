from .Logging import Logging
from .Networking import Networking
from .Filetree import Filetree
from .Maths import Maths
import requests, pickle, json, os, shutil, threading

from PyQt6.QtCore import QObject, pyqtSignal

class Cache():

    CacheFolder = ""
    LethalCompanyPackageIndex = ""
    LethalPackageCache = ""
    ModCache = ""
    Packages = {}
    SelectedModpack = ""
    LoadedMods = {}
    StartCache = False

    def __init__(self,CacheFolder):

        Logging.New("Starting caching system...",'startup')
        Cache.CacheFolder = CacheFolder
        Cache.LethalCompanyPackageIndex = f"{CacheFolder}/lethal_company_package_index.json"
        Cache.LethalPackageCache = f"{CacheFolder}/lethal_package_cache.pk1"
        Cache.ModCache = f"{CacheFolder}/ModCache"

        if not os.path.exists(Cache.LethalCompanyPackageIndex):
            Cache.StartCache = True
            #Cache.Download()
         
        if not os.path.exists(Cache.LethalPackageCache): # If no cache pk1 file is found, create one
            Cache.StartCache = True
            #Cache.Index()
            #Cache.SaveIndex()
    
        else: # Load existing pk1 cache file
            Cache.Packages = Cache.LoadIndex()
        
        if not os.path.exists(Cache.ModCache):
            os.mkdir(Cache.ModCache)

        return
    
    def Download(cache_status_func=None):
        """Downloads the latest cache file from the Thunderstore CDN"""
        Logging.New("Downloading the latest cache")

        Networking.DownloadFromUrl("https://thunderstore.io/c/lethal-company/api/v1/package/",f"{Cache.CacheFolder}/lethal_company_package_index.json",cache_status_func)
    
    def Index(cache_status_func=None):
        """Indexes the cache file into memory, packages can be retrieved using the [author] [name] format"""
        Logging.New("Beginning package index process, this might take a while...")
        if callable(cache_status_func): cache_status_func(f"Caching mods...")
        Cache.Packages.clear()
        if os.path.exists(Cache.LethalCompanyPackageIndex):
            with open(Cache.LethalCompanyPackageIndex, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for entry in data:
                    key = (entry['owner'], entry['name'])
                    Cache.Packages[key] = entry
                Logging.New("Finished Caching")
        return
    
    def SaveIndex():
        """Saves the current memory index into a file"""
        with open(Cache.LethalPackageCache, 'wb') as file:
            pickle.dump(Cache.Packages, file)
        Logging.New("Saved package index to pk1 file")
    
    def LoadIndex():
        """Loads the previous index into memory"""
        with open(Cache.LethalPackageCache, 'rb') as file:
            return pickle.load(file)
        
        Logging.New("Load package index from pk1 file")
        
        return {}
    
    def Reset():
        Cache.Packages.clear()
        try:
            os.remove(Cache.LethalCompanyPackageIndex)
            os.remove(Cache.LethalPackageCache)
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
        return os.path.exists(Cache.LethalCompanyPackageIndex)

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