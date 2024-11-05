from .Networking import Networking
from .Logging import Logging
from .Cache import Cache
from .Filetree import Filetree

import os, shutil, json

class Thunderstore:

        def DownloadPackage(author,mod,mod_version,download_folder,feedback_func=None,text_output_func=None):
            """Downloads a package from Thunderstore given the proper information and returns a filepath"""

            if not os.path.exists(download_folder):
                Logging.New("Please make sure you specify a download location!", 'error')
                return ""

            download_link = f"https://thunderstore.io/package/download/{author}/{mod}/{mod_version}"
            zip_name = f"{author}-{mod}-{mod_version}.zip"
            package_file = os.path.join(download_folder,zip_name)

            Networking.DownloadFromUrl(download_link,package_file,feedback_func=feedback_func,print_length=text_output_func)

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
        
        def DownloadBepInEx(download_folder,loop_count=0):
            """Downloads and decompresses a BepInEx install to a specified location"""

            if loop_count > 20:
                Logging.New("Loop count over 20, cancelling!", 'error')
            
            loop_count = loop_count + 1

            if not os.path.exists(download_folder):
                Logging.New("Please enter a valid path to download the BepInEx file too!",'error')
                return
            
            try:
                bepinex_version = Cache.Get("BepInEx","BepInExPack")['version_number']
            except TypeError:
                bepinex_version = "5.4.2100"
            
            bepinex = Thunderstore.DownloadPackage("BepInEx","BepInExPack",bepinex_version,download_folder)
            bepinex = Filetree.DecompressZip(bepinex)

            try:
                for file in os.listdir(bepinex+"/BepInExPack"):
                    shutil.move(f"{bepinex}/BepInExPack/{file}",os.path.join(download_folder,file))
            except FileNotFoundError:
                shutil.rmtree(bepinex)
                Thunderstore.DownloadBepInEx(download_folder,loop_count)
            
            os.makedirs(f"{download_folder}/BepInEx/plugins")
            
            shutil.rmtree(bepinex)

            return
        
        def Download(url=None,author=None,mod=None,mod_version="",feedback_func=None,text_output_func=None):
            """Extracts a mod from a URL and downloads it to the currently selected modpack, returns the packages location, author, name, version, and new files"""
            
            if not os.path.exists(Cache.SelectedModpack):
                Logging.New("Please select a modpack first!",'error')
                return "", "", "", {}
            
            if not url:
                if not author or not mod or not mod_version.strip():
                    Logging.New("Please provide either a URL or mod info!",'error')
                    return "", "", "", {}
            
            if url:
                author, mod, mod_version = Thunderstore.Extract(url)
                mod_cache_package = Cache.Get(author,mod,mod_version)
                target_mod_version = mod_cache_package['version_number']
            else:
                target_mod_version = mod_version

            package = Thunderstore.PackageSafteyDownload(author,mod,target_mod_version,feedback_func,text_output_func=text_output_func)

            Logging.New(f"{author}-{mod} download has completed, starting next step")
            return package, author, mod, target_mod_version, Filetree.SortFiles(Cache.SelectedModpack,package)
        
        def PackageSafteyDownload(author,mod,target_mod_version,feedback_func,loop_count=0,text_output_func=None):
            loop_count = loop_count + 1

            if loop_count > 20:
                Logging.New("Saftey Download FAILED, loop count was over 20!",'error')
                return None
            if Cache.FileCache.IsCached(author,mod,target_mod_version):
                package = shutil.copy(Cache.FileCache.Get(author,mod,target_mod_version),f"{Cache.SelectedModpack}/BepInEx/plugins/{author}-{mod}-{target_mod_version}.zip")
            else:
                package = Thunderstore.DownloadPackage(author,mod,target_mod_version,f"{Cache.SelectedModpack}/BepInEx/plugins",feedback_func,text_output_func)
                Cache.FileCache.AddMod(package)
            
            package = Filetree.DecompressZip(package)
            
            if not os.path.exists(package):
                Logging.New(f"Corrupted zip file found, redownloading {package} iter {loop_count}", 'warning')
                Cache.FileCache.DeleteMod(author,mod,target_mod_version)
                Thunderstore.PackageSafteyDownload(author,mod,target_mod_version,feedback_func,loop_count,text_output_func)
            
            return package