from .Logging import Logging
from .Time import Time
from .Thunderstore import Thunderstore
from .Cache import Cache
from .Util import Util
from .Networking import Networking
from .QueueMan import QueueMan
from .Filetree import Filetree
import os, json, shutil, threading, gdown

class Modpacks:

    ModpackFolder = ""

    ModpackData = {}

    def __init__(self, ModpacksFolder):
        Logging.New("Starting modpack system...",'startup')
        Modpacks.ModpackFolder = ModpacksFolder
        return
    
    def New(author,name,modpack_version="1.0.0"):
        
        modpack_location = Modpacks.Path(author,name)
        
        if os.path.exists(modpack_location):
            Logging.New("A modpack with this name exists already!",'warning')
            return ""
        
        os.mkdir(modpack_location)
        Modpacks.CreateJson(author,name,modpack_version,modpack_location)
        Thunderstore.DownloadBepInEx(modpack_location)

        return
    
    def CreateJson(author,name,modpack_version,modpack_location):
        modpack_metadata = {
            "author": author,
            "name": name,
            "version": modpack_version,
            "update_date": Time.CurrentDate(),
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

    def Export(author,name):
        export_json_loc = f"{Modpacks.Path(author,name)}/{author}-{name}.json"
        modpack_json = Modpacks.GetJson(author,name)

        export_data = {
            "author": author,
            "name": name,
            "version": modpack_json['version'],
            "update_date": modpack_json['update_date'],
            "cache_timestamp": os.path.getmtime(f"{Cache.CacheFolder}/lethal_company_package_index.json"),
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
    
    def Setup(modpack_data):

        Modpacks.ModpackData = modpack_data

        if Time.IsOlder(os.path.getmtime(f"{Cache.CacheFolder}/lethal_company_package_index.json"),modpack_data['cache_timestamp']):
            Cache.Update()

        Modpacks.New(modpack_data['author'],modpack_data['name'],modpack_data['version'])
        Modpacks.Select(modpack_data['author'],modpack_data['name'])

        QueueMan.QueuePackages(modpack_data['contents']['thunderstore_packages'])
        
        threading.Thread(target=QueueMan.Start(overrides_function=Modpacks.DownloadOverrides),daemon=True).start()

        # Overrides
        
        return
    
    def DownloadOverrides(update=False):
        
        modpack_data = Modpacks.ModpackData
        download_loc = f"{Cache.SelectedModpack}/override.zip"
        preexisting_data = Util.OpenJson(f"{Cache.SelectedModpack}/modpack.json")
        if modpack_data['contents']['overrides']:
            for override in modpack_data['contents']['overrides']:

                if update and override in preexisting_data['overrides']:
                    Logging.New(f"{override} is already installed, skipping!")
                    continue

                if not override['gdrive'] and not override['dropbox']:
                    Logging.New("No valid links found, skipping!")
                    continue

                gd_file = Networking.DownloadFromGoogleDrive(override['gdrive'],download_loc)
                if gd_file == "too_many_requests" or gd_file == "invalid":
                    dropbox = override['dropbox']
                    if str(dropbox).endswith("&dl=0"):
                        dropbox = str(dropbox).replace("&dl=0","&dl=1")

                    Networking.DownloadFromUrl(dropbox,download_loc)
                
                preexisting_data['overrides'].append(override)

                Filetree.DecompressZip(download_loc,Cache.SelectedModpack)

                Util.WriteJson(f"{Cache.SelectedModpack}/modpack.json",preexisting_data)
        
        Modpacks.ModpackData = {}

    def ScanForUpdates():

        if not os.path.exists(Cache.SelectedModpack):
            Logging.New("Please select a modpack first!")
            return
        
        if not Cache.Exists():
            Logging.New("Cannot run updater without having files cached, please cache and try again!")
            return
        
        for mod in Cache.LoadedMods:
            mod_json = Util.OpenJson(Cache.LoadedMods[mod]['json_file'])
            mod_json['has_updates'] = Modpacks.Mods.CheckForUpdates(mod_json['author'],mod_json['name'])
            Util.WriteJson(Cache.LoadedMods[mod]['json_file'],mod_json)

        return

    def Import(modpack):
        """Given a URL or a filepath it will import/update a modpack!"""

        modpack_data = Util.UrlPathDecoder(modpack)
        
        if os.path.exists(Modpacks.Path(modpack_data['author'],modpack_data['name'])):
            if Networking.CompareVersions(modpack_data['version'],Modpacks.GetJson(modpack_data['author'],modpack_data['name'])['version']):
                Logging.New("Triggering update sequence")
                Modpacks.Update(modpack_data['author'],modpack_data['name'],modpack_data)
            else:
                Logging.New("No updates for this modpack!")
                return
        else:
            Modpacks.Setup(modpack_data)

    def Update(author,name,new_data):
        Modpacks.Select(author,name)
        QueueMan.ClearQueue()

        Modpacks.ModpackData = new_data

        for mod in new_data['contents']['thunderstore_packages']:

            if Modpacks.Mods.Installed(mod['author'],mod['name']): # If the mod is already installed update it
                Modpacks.Mods.Update(mod['author'],mod['name'],mod['version'])

            else: # Otherwise queue it up for download
                QueueMan.QueuePackage(mod['author'],mod['name'],mod['version'])

        threading.Thread(target=QueueMan.Start(overrides_function=Modpacks.DownloadOverrides,update=True),daemon=True).start() #Start update process
        
        modpack_json = Modpacks.GetJson(author,name)
        modpack_json['version'] = new_data['version']
        Modpacks.WriteJson(author,name,modpack_json)

        return

    def List():
        modpack_json_paths = []
        for file in os.listdir(Modpacks.ModpackFolder):
            if os.path.isdir(f"{Modpacks.ModpackFolder}/{file}") and os.path.exists(f"{Modpacks.ModpackFolder}/{file}/modpack.json"):
                modpack_json = Util.OpenJson(f"{Modpacks.ModpackFolder}/{file}/modpack.json")
                modpack_json['mod_count'] = Modpacks.GetModCount(modpack_json['author'],modpack_json['name'])
                modpack_json_paths.append(modpack_json)

        return modpack_json_paths

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
        
        def Add(url=None,author=None,mod=None,mod_version="",ignore_dependencies=False):
            if not os.path.exists(Cache.SelectedModpack):
                Logging.New("Please select a modpack first!", 'error')
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

            mod_location, author, name, mod_version, mod_files = Thunderstore.Download(url,author,mod,mod_version)
            Modpacks.Mods.AddPackageFiles(author,name,mod_version,mod_files)
            Modpacks.Mods.LoadMod(mod_location)

            if not ignore_dependencies:
                Logging.New(Modpacks.Mods.Dependencies(author,name))
        
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

            valid_names = ["plugins","config","core","patcher"]

            for file in mod_data['files']:
                if str(file).split("\\")[0].lower() in valid_names:
                    os.remove(f"{Cache.SelectedModpack}/BepInEx/{file}")

                elif str(file).split("\\")[0].lower() == "bepinex":
                    os.remove(f"{Cache.SelectedModpack}/{file}")

                else:
                    os.remove(f"{mod_path}/{file}")

            shutil.rmtree(mod_path)
            
            Modpacks.Mods.UnloadMod(author,name)
        
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

        def CheckForUpdates(author, name):

            if not Modpacks.Mods.Installed(author, name):
                Logging.New(f"Invalid mod, [{author}-{name}] isn't installed!")
                return False
            
            cur_mod_data = Modpacks.Mods.Json(author,name)

            latest_data = Cache.Get(author,name)

            return Networking.CompareVersions(latest_data['version_number'],cur_mod_data['mod_version'])
        
        def GetVersion(author, name):
            return Modpacks.Mods.Json(author,name)["mod_version"]

        def Update(author,name,mod_version=""):

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
            Modpacks.Mods.Add(f"https://thunderstore.io/c/lethal-company/p/{author}/{name}/{mod_version}")

            Logging.New(f"Finished updating [{author}-{name}]")
        
        def OpenURL(author,name):

            Networking.OpenURL(Modpacks.Mods.Json(author,name)['url'])
        
        def Toggle(author,name):
            
            mod_json = Modpacks.Mods.Json(author,name)
            cur_state = mod_json['enabled']
            valid_names = ["plugins","config","core","patcher"]
            mod_path = Modpacks.Mods.Path(author,name,Modpacks.Mods.GetVersion(author,name))

            if cur_state:
                for file in mod_json['files']:
                    if str(file).split("\\")[0].lower() in valid_names:
                        os.rename(f"{Cache.SelectedModpack}/BepInEx/{file}",f"{Cache.SelectedModpack}/BepInEx/{file}"+"_disabled")

                    elif str(file).split("\\")[0].lower() == "bepinex":
                        os.rename(f"{Cache.SelectedModpack}/{file}",f"{Cache.SelectedModpack}/{file}"+"_disabled")

                    else:
                        os.rename(f"{mod_path}/{file}",f"{mod_path}/{file}"+"_disabled")
            else:
                for file in mod_json['files']:
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