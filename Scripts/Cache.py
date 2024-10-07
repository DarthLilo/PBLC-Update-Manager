from .Logging import Logging
from .Networking import Networking
import requests, pickle, json, os

class Cache():

    CacheFolder = ""
    LethalCompanyPackageIndex = ""
    LethalPackageCache = ""
    Packages = {}
    SelectedModpack = ""

    def __init__(self,CacheFolder):

        Logging.New("Starting caching system...",'startup')
        Cache.CacheFolder = CacheFolder
        Cache.LethalCompanyPackageIndex = f"{CacheFolder}/lethal_company_package_index.json"
        Cache.LethalPackageCache = f"{CacheFolder}/lethal_package_cache.pk1"

        if not os.path.exists(Cache.LethalCompanyPackageIndex):
            Cache.Download()
        
        if not os.path.exists(Cache.LethalPackageCache): # If no cache pk1 file is found, create one

            Cache.Index()
            Cache.SaveIndex()

        else: # Load existing pk1 cache file
            Cache.Packages = Cache.LoadIndex()

        return
    
    def Download():
        """Downloads the latest cache file from the Thunderstore CDN"""
        Logging.New("Downloading the latest cache")

        Networking.DownloadFromUrl("https://thunderstore.io/c/lethal-company/api/v1/package/",f"{Cache.CacheFolder}/lethal_company_package_index.json",True)
    
    def Index():
        """Indexes the cache file into memory, packages can be retrieved using the [author] [name] format"""
        Logging.New("Beginning package index process, this might take a while...")
        with open(Cache.LethalCompanyPackageIndex, 'r', encoding='utf-8') as file:
            data = json.load(file)

            for entry in data:
                key = (entry['owner'], entry['name'])
                Logging.New(f"Caching {key}...")
                Cache.Packages[key] = entry
            
            Logging.New("Finished Caching")
    
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

    def Get(owner,name,version="",full_package=False):
        """Gets the matching package entry for the owner and name specified, if a version is specified it will return the entry for that version"""
        key = (owner, name)

        if version.strip():
            packages = Cache.Packages.get(key)['versions']
            for package in packages:
                if package['version_number'] == version:
                    return package
                
            Logging.New(f"No matching version found: [{owner}-{name}-{version}]",'warning')

            return {}
        
        if full_package:
            return Cache.Packages.get(key)
        
        return Cache.Packages.get(key)['versions'][0]
    

                