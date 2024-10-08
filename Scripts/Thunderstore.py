from .Networking import Networking
from .Logging import Logging
from .Cache import Cache
from .Filetree import Filetree

import os, shutil, json

class Thunderstore:

        def DownloadPackage(author,mod,mod_version,download_folder):
            """Downloads a package from Thunderstore given the proper information and returns a filepath"""

            if not os.path.exists(download_folder):
                Logging.New("Please make sure you specify a download location!", 'error')
                return ""

            download_link = f"https://thunderstore.io/package/download/{author}/{mod}/{mod_version}"
            zip_name = f"{author}-{mod}-{mod_version}.zip"
            package_file = os.path.join(download_folder,zip_name)

            Networking.DownloadFromUrl(download_link,package_file)

            return package_file
        
        def Extract(url):
            """Extracts the mod listing from a Thunderstore Link

            Returns 3 strings, Author, Mod, and Mod Version respectively, however, if there is an error at any point it will return False instead"""

            # Verifies the URL and gets list of url segments
            url_segments = Networking.UrlValidator(url)

            # Makes sure something valid returned
            if not url_segments: return False

            if len(url_segments) <= 0:
                return False

            # Mod Data
            try:
                author = url_segments[4]
                mod = url_segments[5]
            except IndexError:
                Logging.New(f"[{url}] is an invalid link, please make sure you copied everything!",'warning')
                return False

            try:
                mod_version = url_segments[6].strip()
            except IndexError:
                mod_version = ""

            return author, mod, mod_version
        
        def DownloadBepInEx(download_folder):
            """Downloads and decompresses a BepInEx install to a specified location"""
            if not os.path.exists(download_folder):
                Logging.New("Please enter a valid path to download the BepInEx file too!",'error')
                return
            
            bepinex = Thunderstore.DownloadPackage("BepInEx","BepInExPack",Cache.Get("BepInEx","BepInExPack")['version_number'],download_folder)
            bepinex = Filetree.DecompressZip(bepinex)

            for file in os.listdir(bepinex+"/BepInExPack"):
                shutil.move(f"{bepinex}/BepInExPack/{file}",download_folder)
            
            os.makedirs(f"{download_folder}/BepInEx/plugins")
            
            shutil.rmtree(bepinex)

            return
        
        def Download(url=None,author=None,mod=None,mod_version=""):
            """Extracts a mod from a URL and downloads it to the currently selected modpack, returns the packages location, author, name, version, and new files"""
            
            if not os.path.exists(Cache.SelectedModpack):
                Logging.New("Please select a modpack first!",'error')
                return
            
            if not url:
                if not author or not mod:
                    Logging.New("Please provide either a URL or mod info!",'error')
                    return
            
            if url:
                author, mod, mod_version = Thunderstore.Extract(url)

            cache_package = Cache.Get(author,mod,mod_version)
            
            package = Thunderstore.DownloadPackage(author,mod,cache_package['version_number'],f"{Cache.SelectedModpack}/BepInEx/plugins")
            package = Filetree.DecompressZip(package)

            return package, author, mod, cache_package['version_number'], Filetree.SortFiles(package)