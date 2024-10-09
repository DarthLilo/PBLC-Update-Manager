from .Logging import Logging
from .Time import Time
from .Thunderstore import Thunderstore
from .Cache import Cache
from .Util import Util
from .Networking import Networking
import os, json, shutil

class Modpacks:

    ModpackFolder = ""
    def __init__(self, ModpacksFolder):
        Logging.New("Starting modpack system...",'startup')
        Modpacks.ModpackFolder = ModpacksFolder
        return
    
    def New(author,name):
        
        modpack_location = Modpacks.Path(author,name)
        
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
            "update_date": Time.CurrentDate(),
        }

        with open(f"{modpack_location}/modpack.json",'w') as modpack_json:
            modpack_json.write(json.dumps(modpack_metadata,indent=4))


        return
    
    def GetJson(author,name):
        return Util.OpenJson(f"{Modpacks.Path(author,name)}/modpack.json")

    def Select(author,name):
        if not os.path.exists(Modpacks.Path(author,name)):
            Logging.New(f"Modpack {author}-{name} not found!",'error')
            return
        Cache.LoadedMods.clear()
        Cache.SelectedModpack = Modpacks.Path(author,name)
        Logging.New(f"Selected modpack {author}-{name}!")
        Modpacks.LoadActiveMods(author,name)
    
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
    
    def Export(author,name):
        export_json_loc = f"{Modpacks.Path(author,name)}/{author}-{name}.json"
        modpack_json = Modpacks.GetJson(author,name)

        export_data = {
            "author": author,
            "name": name,
            "version": modpack_json['version'],
            "update_date": modpack_json['update_date'],
            "contents": {
                "thunderstore_packages": [],
                "overrides": []
            },
            "reinstall": False
        }

        for mod in Cache.LoadedMods:
            mod_json = Util.OpenJson(Cache.LoadedMods[mod]['json_file'])
            export_data['contents']['thunderstore_packages'].append({"author": mod_json['author'],"name": mod_json['name'],"mod_version": mod_json['mod_version']})



        Util.WriteJson(export_json_loc,export_data)

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
            mod_json['files'] = files

            Util.WriteJson(target_mod_json,mod_json)

            return
        
        def Add(url):
            if not os.path.exists(Cache.SelectedModpack):
                Logging.New("Please select a modpack first!", 'error')
                return

            mod_location, author, name, mod_version, mod_files = Thunderstore.Download(url)
            Modpacks.Mods.AddPackageFiles(author,name,mod_version,mod_files)
            Modpacks.Mods.LoadMod(mod_location)
        
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

        def Installed(author,name):
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
            
            Logging.New(f"Updating [{author}-{name}]...")
            
            Modpacks.Mods.Delete(author,name,Modpacks.Mods.GetVersion(author,name))
            Modpacks.Mods.Add(f"https://thunderstore.io/c/lethal-company/p/{author}/{name}/{mod_version}")

            Logging.New(f"Finished updating [{author}-{name}]")