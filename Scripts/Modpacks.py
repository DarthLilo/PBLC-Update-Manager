from .Logging import Logging
from .Time import Time
from .Thunderstore import Thunderstore
from .Cache import Cache
from .Util import Util
from .Networking import Networking
from .QueueMan import QueueMan
from .Filetree import Filetree
from time import sleep
import os, json, shutil, threading, gdown, traceback
from packaging import version

from PyQt6.QtCore import QObject, pyqtSignal

class Modpacks:

    ModpackFolder = ""
    ModpackData = {}
    UpdatePercentageFunc = None
    UpdateThreadDisplay = None
    CloseDownloadScreenFunc = None
    CacheLoadingScreenFunc = None
    SetGlobalPercent = None
    SetCacheStatus = None
    CacheToModpack = None
    ShowDownloadScreen = None
    ShowLoadingScreen = None
    LoadingToEdit = None
    DeselectModpack = None
    RefreshModpacks = None
    ShowModpackSelection = None

    def __init__(self, ModpacksFolder):
        Logging.New("Starting modpack system...",'startup')
        Modpacks.ModpackFolder = ModpacksFolder
        return
    
    def New(author,name,modpack_version="1.0.0",online_link="",icon=""):
        
        modpack_location = Modpacks.Path(author,name)
        
        if os.path.exists(modpack_location):
            Logging.New("A modpack with this name exists already!",'warning')
            return ""
        
        os.mkdir(modpack_location)
        Modpacks.CreateJson(author,name,modpack_version,modpack_location,online_link,icon)
        Thunderstore.DownloadBepInEx(modpack_location)

        if Networking.IsURL(icon):
            Networking.DownloadURLImage(icon,f"{Modpacks.Path(author,name)}/icon.png")
        elif os.path.exists(icon):
            Modpacks.CopyIcon(author,name,icon)

        return
    
    def CopyIcon(author,name,icon_path):
        modpack_path = Modpacks.Path(author,name)
        shutil.copy(icon_path,f"{modpack_path}/icon.png")
    
    def CreateJson(author,name,modpack_version,modpack_location,online_link,icon):
        modpack_metadata = {
            "author": author,
            "name": name,
            "version": modpack_version,
            "update_date": Time.CurrentDate(),
            "online_link": online_link,
            "icon_url": icon,
            "overrides": []
        }

        with open(f"{modpack_location}/modpack.json",'w') as modpack_json:
            modpack_json.write(json.dumps(modpack_metadata,indent=4))


        return
    
    def GetJson(author,name):
        return Util.OpenJson(f"{Modpacks.Path(author,name)}/modpack.json")

    def WriteJson(author,name,data):
        Util.WriteJson(f"{Modpacks.Path(author,name)}/modpack.json",data)

    def Select(author,name):
        if not os.path.exists(Modpacks.Path(author,name)):
            Logging.New(f"Modpack {author}-{name} not found!",'error')
            return
        Cache.LoadedMods.clear()
        Cache.SelectedModpack = Modpacks.Path(author,name)
        Logging.New(f"Selected modpack {author}-{name}!")
        Modpacks.LoadActiveMods(author,name)
    
    def Deselect():
        Cache.LoadedMods.clear()
        Cache.SelectedModpack = ""
        Logging.New("Deselected current modpack")
    
    def Delete(author,name):

        target_modpack = Modpacks.Path(author,name)
        if os.path.exists(target_modpack):
            shutil.rmtree(target_modpack)
        return
    
    def Path(author,name):
        return f"{Modpacks.ModpackFolder}/{author}-{name}"
    
    def LoadActiveMods(author,name):
        plugins_folder = f"{Cache.SelectedModpack}/BepInEx/plugins"
        for file in os.listdir(plugins_folder):
            if os.path.isdir(f"{plugins_folder}/{file}") and os.path.exists(f"{plugins_folder}/{file}/mod.json"):
                Modpacks.Mods.LoadMod(f"{plugins_folder}/{file}")
    
    def GetModCount(author,name):
        mod_count = 0
        plugins_folder = f"{Modpacks.Path(author,name)}/BepInEx/plugins"
        for file in os.listdir(plugins_folder):
            if os.path.isdir(f"{plugins_folder}/{file}") and os.path.exists(f"{plugins_folder}/{file}/mod.json"):
                mod_count += 1
        return mod_count
    
    def ListMods(author,name):
        mods = []
        plugins_folder = f"{Modpacks.Path(author,name)}/BepInEx/plugins"
        for file in os.listdir(plugins_folder):
            if os.path.isdir(f"{plugins_folder}/{file}") and os.path.exists(f"{plugins_folder}/{file}/mod.json"):
                mod_json_data = Util.OpenJson(f"{plugins_folder}/{file}/mod.json")
                mod_json_data['icon_path'] = f"{plugins_folder}/{file}/icon.png"
                mods.append(mod_json_data)
        sorted_mods = sorted(mods,key=lambda mod: mod['name'])
        return sorted_mods

    def Export(author,name):
        export_json_loc = f"{Modpacks.Path(author,name)}/{author}-{name}.json"
        modpack_json = Modpacks.GetJson(author,name)

        export_data = {
            "author": author,
            "name": name,
            "version": modpack_json['version'],
            "update_date": modpack_json['update_date'],
            "cache_timestamp": os.path.getmtime(f"{Cache.CacheFolder}/lethal_company_package_index.json"),
            "online_link": modpack_json['online_link'],
            "icon_url": modpack_json['icon_url'],
            "contents": {
                "thunderstore_packages": [],
                "overrides": []
            },
            "reinstall": False
        }

        for mod in Cache.LoadedMods:
            mod_json = Util.OpenJson(Cache.LoadedMods[mod]['json_file'])
            export_data['contents']['thunderstore_packages'].append({"author": mod_json['author'],"name": mod_json['name'],"version": mod_json['mod_version']})



        Util.WriteJson(export_json_loc,export_data)

        return
    
    def Setup(modpack_data,finish_func):
        QueueMan.ClearQueue()

        Modpacks.ModpackData = modpack_data

        Modpacks.New(modpack_data['author'],modpack_data['name'],modpack_data['version'],modpack_data['online_link'],modpack_data['icon_url'])
        Modpacks.Select(modpack_data['author'],modpack_data['name'])

        QueueMan.QueuePackages(modpack_data['contents']['thunderstore_packages'])
        Modpacks.DownloadManagement.StartWorkerObject(finish_func=finish_func)

        # Overrides
        
        return
    
    def DownloadOverrides(update=False,closeSignalFunc=None,downloadScreenFunc=None,finish_func=None):
        
        # Swap to loading screen

        if callable(downloadScreenFunc): downloadScreenFunc("Downloading Overrides")

        modpack_data = Modpacks.ModpackData
        download_loc = f"{Cache.SelectedModpack}/override.zip"
        preexisting_data = Util.OpenJson(f"{Cache.SelectedModpack}/modpack.json")
        if "contents" in modpack_data:
            if modpack_data['contents']['overrides']:
                for override in modpack_data['contents']['overrides']:

                    if update and override in preexisting_data['overrides']:
                        Logging.New(f"{override} is already installed, skipping!")
                        continue

                    if not override['gdrive'] and not override['dropbox']:
                        Logging.New("No valid links found, skipping!")
                        continue
                    try:
                        gd_file = Networking.DownloadFromGoogleDrive(override['gdrive'],download_loc)
                        if gd_file == "too_many_requests" or gd_file == "invalid":
                            dropbox = override['dropbox']
                            if str(dropbox).endswith("&dl=0"):
                                dropbox = str(dropbox).replace("&dl=0","&dl=1")

                            Networking.DownloadFromUrl(dropbox,download_loc)
                    except Exception as e:
                        Logging.New(traceback.format_exc(),'error')
                        modpack_data['contents']['overrides'].append(override)

                    preexisting_data['overrides'].append(override)

                    Filetree.DecompressZip(download_loc,Cache.SelectedModpack)

                    Util.WriteJson(f"{Cache.SelectedModpack}/modpack.json",preexisting_data)

        Modpacks.ModpackData = {}
        Logging.New("Finished modpack download, starting closure proceedures")
        
        if callable(closeSignalFunc): closeSignalFunc()
        if callable(finish_func): finish_func()

        #Modpacks._screenFinishUpdate()

    def ScanForUpdates():

        if not os.path.exists(Cache.SelectedModpack):
            Logging.New("Please select a modpack first!")
            return
        
        if not Cache.Exists():
            Logging.New("Cannot run updater without having files cached, please cache and try again!")
            return
        
        for mod in Cache.LoadedMods:
            mod_json = Util.OpenJson(Cache.LoadedMods[mod]['json_file'])
            has_updates = Modpacks.Mods.CheckForUpdates(mod_json['author'],mod_json['name'])
            if has_updates:
                mod_json['has_updates'] = Cache.Get(mod_json['author'],mod_json['name'])['version_number']
                Util.WriteJson(Cache.LoadedMods[mod]['json_file'],mod_json)

        return

    def UpdateVerify(author,name,finish_func=None):
        modpack_json = Modpacks.GetJson(author,name)
        if modpack_json['online_link']:
            Modpacks.ImportVerify(modpack_json['online_link'],Modpacks.ShowDownloadScreen,Modpacks.CacheLoadingScreenFunc,Modpacks.SetCacheStatus,finish_func)
        else:
            Logging.New("No valid update path linked, skipping")
            if callable(finish_func): finish_func()

    def ImportVerify(modpack, showdownloadfunc=None,cacheloadingfunc=None,cachestatusfunc=None,finish_func=None):
        """Given a URL or a filepath it will import/update a modpack!"""
        
        modpack_data = Util.UrlPathDecoder(modpack)

        if Time.IsOlder(os.path.getmtime(f"{Cache.CacheFolder}/lethal_company_package_index.json"),modpack_data['cache_timestamp']):
            if callable(cacheloadingfunc): cacheloadingfunc()
            Cache.Update(lambda modpack_data=modpack, download_func = showdownloadfunc, finishfunc=finish_func :Modpacks.Import(modpack_data,download_func,finishfunc),  cache_status_func=cachestatusfunc)
        else:
            Modpacks.Import(modpack,showdownloadfunc,finish_func)

    def Import(modpack, showdownloadfunc=None,finish_func=None):
        """Given a URL or a filepath it will import/update a modpack!"""

        Logging.New("Importing modpack!")

        modpack_data = Util.UrlPathDecoder(modpack)
        
        if os.path.exists(Modpacks.Path(modpack_data['author'],modpack_data['name'])):
            if Networking.CompareVersions(modpack_data['version'],Modpacks.GetJson(modpack_data['author'],modpack_data['name'])['version']):
                Logging.New("Triggering update sequence")
                if callable(showdownloadfunc): showdownloadfunc()
                Modpacks.Update(modpack_data['author'],modpack_data['name'],modpack_data,finish_func)
            else:
                Logging.New("No updates for this modpack!")
                if callable(finish_func): finish_func()
                return
        else:
            if callable(showdownloadfunc): showdownloadfunc()
            Modpacks.Setup(modpack_data,finish_func)

    def Update(author,name,new_data,finish_func=None):
        Modpacks.Select(author,name)
        QueueMan.ClearQueue()

        Modpacks.ModpackData = new_data

        verify_mod_cache = []
        for mod in new_data['contents']['thunderstore_packages']:
            verify_mod_cache.append(f"{mod['author']}-{mod['name']}")
        
        delete_queue = []
        for mod in Cache.LoadedMods:
            if mod not in verify_mod_cache:
                delete_queue.append(mod)
        
        for mod in delete_queue:
            split = mod.split("-")
            Modpacks.Mods.Delete(split[0],split[1])

        for mod in new_data['contents']['thunderstore_packages']:

            if Modpacks.Mods.Installed(mod['author'],mod['name']): # If the mod is already installed update it
                if Networking.CompareVersions(mod['version'],Modpacks.Mods.GetVersion(mod['author'],mod['name'])):
                    Modpacks.Mods.Delete(mod['author'],mod['name'])
                    QueueMan.QueuePackage(mod['author'],mod['name'],mod['version'])
                #Modpacks.Mods.Update(mod['author'],mod['name'],mod['version'])

            else: # Otherwise queue it up for download
                QueueMan.QueuePackage(mod['author'],mod['name'],mod['version'])

        Modpacks.DownloadManagement.StartWorkerObject(update=True,finish_func=finish_func)
        
        modpack_json = Modpacks.GetJson(author,name)
        modpack_json['version'] = new_data['version']
        Modpacks.WriteJson(author,name,modpack_json)

        return

    def List():
        modpack_json_paths = []
        for file in os.listdir(Modpacks.ModpackFolder):
            if os.path.isdir(f"{Modpacks.ModpackFolder}/{file}") and os.path.exists(f"{Modpacks.ModpackFolder}/{file}/modpack.json"):
                modpack_json = Util.OpenJson(f"{Modpacks.ModpackFolder}/{file}/modpack.json")
                modpack_icon = f"{Modpacks.ModpackFolder}/{file}/icon.png"
                modpack_json['mod_count'] = Modpacks.GetModCount(modpack_json['author'],modpack_json['name'])
                modpack_json['icon'] = modpack_icon
                modpack_json_paths.append(modpack_json)

        return modpack_json_paths
    
    def Exists(author,name):
        modpack_path = Modpacks.Path(author,name)
        if not os.path.exists(modpack_path):
            return False
        
        return os.path.exists(f"{modpack_path}/modpack.json")

    def Verify(modpack_data):
        Modpacks.Select(modpack_data['author'],modpack_data['name'])

        QueueMan.ClearQueue()

        # Deleting extra mods
        verify_mod_cache = []
        for mod in modpack_data['contents']['thunderstore_packages']:
            verify_mod_cache.append(f"{mod['author']}-{mod['name']}")
        
        delete_queue = []
        for mod in Cache.LoadedMods:
            if mod not in verify_mod_cache:
                delete_queue.append(mod)
        
        for mod in delete_queue:
            split = mod.split("-")
            Modpacks.Mods.Delete(split[0],split[1])



        for mod in modpack_data['contents']['thunderstore_packages']:
            if not Modpacks.Mods.Installed(mod['author'],mod['name']):
                QueueMan.QueuePackage(mod['author'],mod['name'],mod['version'])
                #Modpacks.Mods.Add(author=mod['author'],mod=mod['name'],mod_version=mod['version'])
        
        if len(QueueMan.package_queue):
            Modpacks.ShowDownloadScreen()
            Modpacks.DownloadManagement.StartWorkerObject()
        
        Modpacks.DeselectModpack()
        Modpacks.RefreshModpacks()
        
    class DownloadManagement:
        def StartWorkerObject(update=False,finish_func=None,screen_type=0):

            worker_object = QueueWorkerObject()
            worker_object.progress_output.connect(Modpacks.UpdatePercentageFunc)
            worker_object.thread_display_update.connect(Modpacks.UpdateThreadDisplay)
            worker_object.close_download_screen.connect(Modpacks.CloseDownloadScreenFunc)
            worker_object.loading_screen_trigger.connect(Modpacks.CacheLoadingScreenFunc)
            if callable(finish_func):
                worker_object.finish_func.connect(finish_func)

            working_thread = threading.Thread(target=lambda: worker_object.run(update=update,screen_type=screen_type),daemon=True)
            working_thread.start()

            return


    class Mods:
        def Path(author,name,mod_version):
            return f"{Cache.SelectedModpack}/BepInEx/plugins/{author}-{name}-{mod_version}"
        
        def LoadMod(path):
            full_mod_name = os.path.basename(path).split("-")
            author = full_mod_name[0]
            name = full_mod_name[1]

            new_mod = {
                "json_file": f"{path}/mod.json",
                "icon": f"{path}/icon.png",
                }

            Cache.LoadedMods[f"{author}-{name}"] = new_mod

        def UnloadMod(author,name):
            del Cache.LoadedMods[f"{author}-{name}"]

        def AddPackageFiles(author,name,mod_version,files):
            target_mod_json = f"{Modpacks.Mods.Path(author,name,mod_version)}/mod.json"
            mod_json = {}
            mod_json['author'] = author
            mod_json['name'] = name
            mod_json['mod_version'] = mod_version
            mod_json['enabled'] = True
            mod_json['files'] = files
            mod_json['has_updates'] = False
            mod_json['url'] = f"https://thunderstore.io/c/lethal-company/p/{author}/{name}/"

            Util.WriteJson(target_mod_json,mod_json)

            return
        
        def Add(url=None,author=None,mod=None,mod_version="",ignore_dependencies=False,feedback_func=None,text_output_func=None,finished_func=None):
            if not os.path.exists(Cache.SelectedModpack):
                Logging.New("Please select a modpack first!", 'error')
                return
            
            if url and not Networking.UrlValidator(url):
                Logging.New("Please enter a valid link!")
                return

            
            if not url:
                if not author or not mod or not mod_version.strip():
                    Logging.New(f"Not enough mod info to get a download! [{author}-{mod}-{mod_version}]")
                    return

            if url and not Cache.Exists():
                Logging.New("Cannot download from a URL without having the package index! Please cache first!")
                return
            
            if Modpacks.Mods.Installed(author,mod,url):
                Logging.New("This mod is already installed, either update it or delete it!")
                return
            
            if url:
                author, mod, mod_version = Thunderstore.Extract(url)
            
            if not mod_version.strip():
                target_version = Cache.Get(author,mod)['version_number']
            else:
                try:
                    version.parse(mod_version)
                    target_version = mod_version
                except:
                    target_version = Cache.Get(author,mod)['version_number']
                
            if not callable(finished_func):
                finished_func = Modpacks.LoadingToEdit
            
            QueueMan.ClearQueue()
            QueueMan.QueuePackage(author,mod,target_version)
            Modpacks.ShowLoadingScreen()
            Modpacks.DownloadManagement.StartWorkerObject(screen_type=1,finish_func=finished_func)
        
        def Delete(author,name,mod_version=""):
            if not os.path.exists(Cache.SelectedModpack):
                Logging.New("Please select a valid modpack first!",'error')
                return
            
            if not mod_version.strip():
                mod_version = Modpacks.Mods.GetVersion(author,name)

            mod_path = Modpacks.Mods.Path(author,name,mod_version)

            if not os.path.exists(mod_path):
                Logging.New(f"Mod not found! {mod_path}",'error')
                return

            mod_json = f"{mod_path}/mod.json"
            mod_data = Util.OpenJson(mod_json)

            valid_names = ["plugins","config","core","patchers"]

            for file in mod_data['files']:
                try:
                    if str(file).split("\\")[0].lower() in valid_names:
                        os.remove(f"{Cache.SelectedModpack}/BepInEx/{file}")

                    elif str(file).split("\\")[0].lower() == "bepinex":
                        os.remove(f"{Cache.SelectedModpack}/{file}")

                    else:
                        os.remove(f"{mod_path}/{file}")
                except FileNotFoundError:
                    Logging.New(f"File not found! {file}",'warning')

            shutil.rmtree(mod_path)
            
            Modpacks.Mods.UnloadMod(author,name)

            Logging.New(f"Deleted {author}-{name}")
        
        def Json(author,name):
            if f"{author}-{name}" in Cache.LoadedMods:
                return Util.OpenJson(Cache.LoadedMods[f"{author}-{name}"]['json_file'])
            
            return {}
        
        def WriteJson(author,name,data):
            Util.WriteJson(Cache.LoadedMods[f"{author}-{name}"]['json_file'],data)

        def Installed(author=None,name=None,url=None):
            if url:
                author, mod, mod_version = Thunderstore.Extract(url)
            
            return f"{author}-{name}" in Cache.LoadedMods

        def SetUpdateVersion(author,name,new_version):
            mod_json = Modpacks.Mods.Json(author,name)
            mod_json['has_updates'] = new_version
            Modpacks.Mods.WriteJson(author,name,mod_json)

        def CheckForUpdates(author, name):

            if not Modpacks.Mods.Installed(author, name):
                Logging.New(f"Invalid mod, [{author}-{name}] isn't installed!")
                return False
            
            cur_mod_data = Modpacks.Mods.Json(author,name)

            latest_data = Cache.Get(author,name)

            return Networking.CompareVersions(latest_data['version_number'],cur_mod_data['mod_version'])
        
        def GetVersion(author, name):
            return Modpacks.Mods.Json(author,name)["mod_version"]

        def Update(author,name,mod_version="",feedback_func=None,text_output_func=None,finished_func=None):

            if not Modpacks.Mods.Installed(author, name):
                Logging.New(f"Invalid mod, [{author}-{name}] isn't installed!")
                return False
            
            if Modpacks.Mods.GetVersion(author,name) == mod_version:
                Logging.New(f"This version of the mod is already installed!")
                return False
            
            Logging.New(f"Updating [{author}-{name}]...")

            if not Modpacks.Mods.Json(author,name)['enabled']:
                Modpacks.Mods.Toggle(author,name)
            
            Modpacks.Mods.Delete(author,name,Modpacks.Mods.GetVersion(author,name))
            Modpacks.Mods.Add(f"https://thunderstore.io/c/lethal-company/p/{author}/{name}/{mod_version}",feedback_func=feedback_func,text_output_func=text_output_func)

            Logging.New(f"Finished updating [{author}-{name}]")
        
        def OpenURL(author,name):

            Networking.OpenURL(Modpacks.Mods.Json(author,name)['url'])
        
        def Toggle(author,name):
            
            mod_json = Modpacks.Mods.Json(author,name)
            cur_state = mod_json['enabled']
            valid_names = ["plugins","config","core","patchers"]
            mod_path = Modpacks.Mods.Path(author,name,Modpacks.Mods.GetVersion(author,name))

            if cur_state:
                for file in mod_json['files']:
                    if file == "icon.png": continue
                    if str(file).split("\\")[0].lower() in valid_names:
                        os.rename(f"{Cache.SelectedModpack}/BepInEx/{file}",f"{Cache.SelectedModpack}/BepInEx/{file}"+"_disabled")

                    elif str(file).split("\\")[0].lower() == "bepinex":
                        os.rename(f"{Cache.SelectedModpack}/{file}",f"{Cache.SelectedModpack}/{file}"+"_disabled")

                    else:
                        os.rename(f"{mod_path}/{file}",f"{mod_path}/{file}"+"_disabled")
            else:
                for file in mod_json['files']:
                    if file == "icon.png": continue
                    if str(file).split("\\")[0].lower() in valid_names:
                        os.rename(f"{Cache.SelectedModpack}/BepInEx/{file}"+"_disabled",f"{Cache.SelectedModpack}/BepInEx/{file}")

                    elif str(file).split("\\")[0].lower() == "bepinex":
                        os.rename(f"{Cache.SelectedModpack}/{file}"+"_disabled",f"{Cache.SelectedModpack}/{file}",)

                    else:
                        os.rename(f"{mod_path}/{file}"+"_disabled", f"{mod_path}/{file}")

            mod_json['enabled'] = not mod_json['enabled']
            Modpacks.Mods.WriteJson(author,name,mod_json)

            return
        
        def Dependencies(author,name):

            mod_dependencies = Cache.Get(author,name)['dependencies']

            cur_dep = 0
            for dependency in mod_dependencies:
                if str(dependency).__contains__("BepInEx-BepInExPack"):
                    mod_dependencies.remove(dependency)
                cur_dep += 1

            return mod_dependencies

class QueueWorkerObject(QObject):
    thread_display_update = pyqtSignal(int,str,str,str)
    progress_output = pyqtSignal(int, float)
    close_download_screen = pyqtSignal()
    loading_screen_trigger = pyqtSignal(str)
    finish_func = pyqtSignal()

    def run(self,update=False, screen_type=0):

        if screen_type == 0:
            threading.Thread(target=QueueMan.Start(overrides_function=Modpacks.DownloadOverrides,
                                                   emit_method=self.progress_output.emit,
                                                   thread_display_method=self.thread_display_update.emit,
                                                   close_download_method=self.close_download_screen.emit,
                                                   loading_screen_method=self.loading_screen_trigger.emit,
                                                   set_global_percent_method=Modpacks.SetGlobalPercent,
                                                   finish_func=self.finish_func.emit,update=update),daemon=True).start()
        elif screen_type == 1:
            threading.Thread(target=QueueMan.Start(finish_func=self.finish_func.emit,update=update),daemon=True).start()