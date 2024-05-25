import json, os, winreg, vdf, shutil, zipfile,gdown, sys, customtkinter, pyglet, subprocess, progressbar, webbrowser, requests, validators, threading, pyeaze, configobj, time, traceback
from PIL import Image,ImageDraw
from urllib import request
from urllib.error import HTTPError, URLError
from packaging import version
from CTkMessagebox import CTkMessagebox
from CTkToolTip import *
from io import BytesIO

print("Loading...")

pbar = None

PBLC_Update_Manager_Version = "0.3.0"

github_repo_latest_release = "https://api.github.com/repos/DarthLilo/PBLC-Update-Manager/releases/latest"
customtkinter.set_appearance_mode("dark")

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def getCurrentPathLoc():

    if getattr(sys,'frozen',False):
        cur_directory = os.path.dirname(sys.executable)
    else:
        cur_directory = os.path.dirname(__file__)
    
    return cur_directory

pyglet.options['win32_gdi_font'] = True

pyglet.font.add_file(resource_path('assets/3270-Regular.ttf'))


#STARTUP

if sys.platform.startswith('win'):
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'DarthLilo.PBLC_Update_Manager') # Arbitrary string

moddb_file = os.path.join(getCurrentPathLoc(),"data","mod_database.json")

def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None

def read_reg(ep, p = r"", k = ''):
    try:
        key = winreg.OpenKeyEx(ep, p)
        value = winreg.QueryValueEx(key,k)
        if key:
            winreg.CloseKey(key)
        return value[0]
    except Exception as e:
        return None
    return None

def open_json(path):
    with open(path, 'r') as json_opener:
        json_data = json_opener.read()
    json_data = json.loads(json_data)

    return json_data

def clear_dir(dir = ""):
    for folder in os.listdir(dir):
        filepath = os.path.join(dir, folder)
        filepath = os.path.normpath(filepath)
        shutil.rmtree(filepath)

def newEmptyRow(self,row_number,spacing):
        self.empty_row = customtkinter.CTkLabel(self.main_frame, text="")
        self.empty_row.grid(row=row_number, column=0, padx=20, pady=spacing)

def roundImageCorners(source_image, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', source_image.size, 255)
    w, h = source_image.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    source_image.putalpha(alpha)
    return source_image


class settingsMan():
        
    settings_file_path = os.path.normpath(f"{getCurrentPathLoc()}/data/pblc_update_man.ini")

    def generate_settings():
        if not os.path.exists(settingsMan.settings_file_path):
            settingsMan.resetSettingsDefault()

    def resetSettingsDefault():

        #data folder
        if not os.path.exists(os.path.join(getCurrentPathLoc(),"data")):
            os.mkdir(os.path.join(getCurrentPathLoc(),"data"))

        config=configobj.ConfigObj()
        config.filename = settingsMan.settings_file_path
        config.initial_comment = ["PBLC Update Manager Configuration",""]
        

        #CONFIG WRITING

        paths = {
            "version_database": {"value":"","description":"Determines where the program checks for updates. URL or a FILEPATH","default":"","type":"string"},
            "update_instructions" : {"value":"","description":"Folder location of version update files. DIRPATH","default":"","type":"string"},
            "patch_instructions": {"value":"","description":"Determines where the program checks for patches. URL or a FILEPATH","default":"","type":"string"},
            "lethal_company_path": {"value":"","description":"Location of your Lethal Company root folder. DIRPATH","default":"","type":"string"}
        }

        program = {
            "check_for_updates_automatically": {"value": True,"description":"Does the program check for updates automatically on startup and prompt the user?","default":True,"type":"bool"},
            "show_beta_options": {"value":False,"description":"Will the user be able to see the beta options?","default":False,"type":"bool"},
            "enable_mods_menu": {"value": False,"description":"Will the program cache enabled mods on startup or ignore them?","default":False,"type":"bool"}
        }
        
        config['paths'] = paths
        config['program'] = program

        config.comments['paths'] = ["Path related settings, changing these may break the program!"]
        config.comments['program'] = ["","General settings related to the program"]

        config.write()

        return

    def readSettingsValue(container,value,index=0):
        config = configobj.ConfigObj(settingsMan.settings_file_path)
        selections = ['value','description','default','type']
        return config[container][value][selections[index]]

    def writeSettingsValue(container,value,new_value):

        config = configobj.ConfigObj(settingsMan.settings_file_path)

        config[container][value]['value'] = new_value

        config.write()

    def returnSettingsData():
        return configobj.ConfigObj(settingsMan.settings_file_path)

settingsMan.generate_settings()

def locate_lethal_company():

    custom_lethal_path = settingsMan.readSettingsValue("paths","lethal_company_path")
    
    if os.path.exists(custom_lethal_path):
        return custom_lethal_path
    else:
        print("Locating lethal path...")
        steam_install_path = str(read_reg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\\Wow6432Node\\Valve\\Steam", k = 'InstallPath'))
        steamapps = steam_install_path+"\\steamapps"
        library_folders = steamapps+"\\libraryfolders.vdf"
        libdata = vdf.load(open(library_folders))
        lethal_company_steamid = "1966720"

        for library in libdata['libraryfolders']:
            cur_lib = libdata['libraryfolders'][library]
            apps = cur_lib["apps"]
            if lethal_company_steamid in apps:
                lethal_path = os.path.normpath(f"{cur_lib['path']}/steamapps/common/Lethal Company")
                return lethal_path

def download_from_google_drive(source,destination,bar=None):
    print(f"Beginning download of {source} from Google Drive...")
    try:
        gdown.download(id=source,output=destination,bar=bar)
        if bar:
            app.updateProgressCount()
        return "finished"
    except gdown.exceptions.FileURLRetrievalError:
        print("Google Drive file has too many requests, going to Dropbox backup...")
        return "too_many_requests"

def migrate_update_files(source,destination):
    print("Moving files...")
    files = os.listdir(source)

    for file in files:
        file_path = os.path.join(source,file)
        destination_path = os.path.join(destination,file)

        if os.path.exists(destination_path):
            os.remove(destination_path)

        shutil.move(file_path,destination_path)

def move_file(source,dest):
    if os.path.exists(dest):
        os.remove(dest)
    shutil.move(source,dest)
    
LC_Path = locate_lethal_company()
downloads_folder = os.path.normpath(f"{LC_Path}/downloads")
pblc_vers = os.path.normpath(f"{LC_Path}/pblc_version")
bepinex_path = os.path.normpath(f"{LC_Path}/BepInEx")
plugins_folder = os.path.join(bepinex_path,"plugins")
doorstop_path = os.path.normpath(f"{LC_Path}/doorstop_config.ini")
winhttp_path = os.path.normpath(f"{LC_Path}/winhttp.dll")
current_file_loc = getCurrentPathLoc()
default_pblc_vers = {"version": "0.0.0", "beta_version": "0.0.0", "beta_goal": "0.0.0","performance_mode":"off"}
package_data_path = os.path.normpath(f"{current_file_loc}/data/pkg")
isScriptFrozen = getattr(sys, "frozen", False)

# download_override | GDCODE | DROPBOX
# url_add_mod | NAMESPACE | NAME | VERSION
# delete_mod | NAMESPACE | NAME
# update_vers | PATCH_VERSION | VERSION
# download_bepinex
# clean_install

dev_mode = f"{current_file_loc}/data/pooworms"
if not os.path.exists(dev_mode):
    dev_mode = None



def grab_version_db():
    
    default_version_db = "https://raw.githubusercontent.com/DarthLilo/PBLC-Update-Manager/master/version_db.json"
    local_version_db = settingsMan.readSettingsValue("paths","version_database")
    is_url = False
    if validators.url(local_version_db):
        is_url = True
    
    if local_version_db.strip(): #Custom Path
        try:
            if is_url:
                return json.loads(request.urlopen(local_version_db).read().decode())
            else:
                return open_json(local_version_db)
        except:
            print("INVALID VERSION DATABASE")
            return None
    else: #default
        return json.loads(request.urlopen(default_version_db).read().decode())

def grab_patch_instructions():
    default_patch_instruct = "https://raw.githubusercontent.com/DarthLilo/PBLC-Update-Manager/master/patch_instructions.json"
    local_patch_instruct = settingsMan.readSettingsValue("paths","patch_instructions")
    is_url = False
    if validators.url(local_patch_instruct):
        is_url = True
    if local_patch_instruct.strip(): #Custom Path
        try:
            if is_url:
                return json.loads(request.urlopen(local_patch_instruct).read().decode())
            else:
                return open_json(local_patch_instruct)
        except:
            print("INVALID PATCH INSTRUCTIONS")
            return None
    else: #default
        return json.loads(request.urlopen(default_patch_instruct).read().decode())

def grab_update_instructions(version,beta=False):
    
    default_update_instructions = ""#"https://raw.githubusercontent.com/DarthLilo/PBLC-Update-Manager/master/version_db.json"
    local_update_instructions = settingsMan.readSettingsValue("paths","update_instructions")
    is_url = False
    if validators.url(local_update_instructions):
        is_url = True
    
    if local_update_instructions.strip(): #Custom Path
        try:
            if is_url:
                return json.loads(request.urlopen(local_update_instructions).read().decode())
            else:
                return open_json(f"{local_update_instructions}/{version}.json") if not beta else open_json(f"{local_update_instructions}/{version}_beta.json")
        except:
            print("INVALID VERSION DATABASE")
            return None
    else: #default
        return json.loads(request.urlopen(default_update_instructions).read().decode())

def startupFunc():
    cur_folder = getCurrentPathLoc()

    #data folder
    if not os.path.exists(os.path.join(cur_folder,"data")):
        print("New install, creating data folder...")
        os.mkdir(os.path.join(cur_folder,"data"))
    else:
        print("Located data folder.")
    
    if not os.path.exists(plugins_folder):
        os.makedirs(plugins_folder)
    
    
    mod_pkg = os.path.join(cur_folder,"data","pkg")

    if not os.path.exists(moddb_file):
        print("No mod database found, creating one...")
        with open(moddb_file, "w") as moddb_create:
            moddb_create.write(json.dumps({"installed_mods":{},"patch_version":"0.0.0"},indent=4))
    else:
        print("Mod database found.")
    
    if not os.path.exists(mod_pkg):
        os.mkdir(mod_pkg)

startupFunc()

def get_mod_database():
    mod_database = open_json(os.path.join(current_file_loc,"data","mod_database.json"))
    return mod_database


def get_current_version(int_only = False):
    if os.path.exists(pblc_vers):
        cur_vers_json = open_json(pblc_vers)
        if int_only:
            installed_version = int(str(cur_vers_json['version']).replace(".",""))
            try:
                installed_beta_version = int(str(cur_vers_json['beta_version']).replace(".",""))
            except KeyError:
                installed_beta_version = 0
        else:
            installed_version = str(cur_vers_json['version'])
            try:
                installed_beta_version = str(cur_vers_json['beta_version'])
            except KeyError:
                installed_beta_version = "0"
        try:
            performance_mode = cur_vers_json['performance_mode']
        except KeyError:
            performance_mode = "off"
    else:
        cur_vers_json = default_pblc_vers
        installed_version = 0
        installed_beta_version = 0
        performance_mode = "off"
    
    return installed_version,installed_beta_version, cur_vers_json, performance_mode
    
#checking for updates

class PBLC_Icons():
    def download(pathOnly=False):
        if pathOnly:
            return 'assets/download.png'
        return Image.open('assets/download.png')
    
    def arrow_up_right(pathOnly=False):
        if pathOnly:
            return 'assets/arrow_right_up.png'
        return Image.open('assets/arrow_right_up.png')
    
    def archive(pathOnly=False):
        if pathOnly:
            return 'assets/archive.png'
        return Image.open('assets/archive.png')
    
    def checklist(pathOnly=False):
        if pathOnly:
            return 'assets/checklist.png'
        return Image.open('assets/checklist.png')
    
    def refresh(pathOnly=False):
        if pathOnly:
            return 'assets/refresh.png'
        return Image.open('assets/refresh.png')
    
    def save(pathOnly=False):
        if pathOnly:
            return 'assets/save.png'
        return Image.open('assets/save.png')
    
    def trash_can(pathOnly=False):
        if pathOnly:
            return 'assets/trash_can.png'
        return Image.open('assets/trash_can.png')
    
    def uninstall(pathOnly=False):
        if pathOnly:
            return 'assets/uninstall.png'
        return Image.open('assets/uninstall.png')
    
    def website(pathOnly=False):
        if pathOnly:
            return 'assets/website.png'
        return Image.open('assets/website.png')
    
    def checkmark(pathOnly=False):
        if pathOnly:
            return 'assets/checkmark.png'
        return Image.open('assets/checkmark.png')
    
    def info(pathOnly=False):
        if pathOnly:
            return 'assets/info.png'
        return Image.open('assets/info.png')
    
    def missing_icon(pathOnly=False):
        if pathOnly:
            return 'assets/missing_icon.png'
        return Image.open('assets/missing_icon.png')
    
    def lethal_company(pathOnly=False):
        if pathOnly:
            return 'assets/lethal_art.png'
        return Image.open('assets/lethal_art.png')
    

class version_man():

    def install_version(vers):
        if os.path.exists(pblc_vers):
            cur_vers_json = open_json(pblc_vers)
            if vers == "release":
                install_version = cur_vers_json['version']
            elif vers == "beta":
                install_version = cur_vers_json['beta_version']
        else:
            install_version = "0.0.0"
        return install_version

    def get_patch():
        mod_db = get_mod_database()
        try:
            patch_version = mod_db['patch_version']
        except KeyError:
            patch_version = "0.0.0"

        return patch_version
    
    def set_patch(patch):
        mod_db = get_mod_database()
        mod_db['patch_version'] = patch
        with open(moddb_file,"w") as patch_set:
            patch_set.write(json.dumps(mod_db,indent=4))

def decompress_zip(zip_file,destination):
    print("Unzipping file...")
    with zipfile.ZipFile(zip_file, 'r',zipfile.ZIP_DEFLATED) as zip_ref:
        zip_ref.extractall(destination)
    os.remove(zip_file)

def compress_zip(zip_file,files):
    with zipfile.ZipFile(zip_file,'w',zipfile.ZIP_DEFLATED) as zipf:
        try:
            for file_path in files:
                relative_path = os.path.basename(file_path)
                print(f"Compressing {relative_path}...")
                zipf.write(file_path,arcname=relative_path)
        except:
            return "CANCELLED"

def compress_zip_dir(zip_file,dir_path):
    with zipfile.ZipFile(zip_file,'a',zipfile.ZIP_DEFLATED) as zipf:
        for folder, _, files in os.walk(dir_path):
            for file in files:
                absolute_path = os.path.join(folder, file)
                relative_path = os.path.relpath(absolute_path, os.path.dirname(dir_path))
                print(f"Compressing {relative_path}...")
                zipf.write(absolute_path, arcname=relative_path)

def cacheInstructionLen(cache_type,target_version,update_type="release"):
    instruction_len = 0

    if update_type == "release":
        update_instructions = grab_update_instructions(target_version)
    else:
        update_instructions = grab_update_instructions(target_version,True)
    patch_instruct = grab_patch_instructions()
    current_patch = version_man.get_patch()

    if cache_type == "full":
        instruction_len += len(update_instructions['instructions'])
    
    #patch len

    if update_type == "release":
        if target_version in patch_instruct:
            print("found target version in pach")
            for patch in patch_instruct[target_version]['release']:
                if version.Version(patch) > version.Version(current_patch):
                    instruction_len += len(patch_instruct[target_version]['release'][patch])

        #recursive version checking
        for release in patch_instruct:
            if version.Version(release) > version.Version(target_version):
                instruction_len += cacheInstructionLen(cache_type,release)
                break

    print(instruction_len)
    return instruction_len

def decodeDownloadCommand(input_command,bar=None):
    split_commnad = str(input_command).split("|")

    command=split_commnad[0]
    if command == "download_override":
        gdlink = split_commnad[1]
        dropbox = split_commnad[2]
        print("Downloading override files...")
        downloadOverridePatch(gdlink,dropbox)
    elif command == "url_add_mod":
        namespace = split_commnad[1]
        name = split_commnad[2]
        target_vers = split_commnad[3]
        if not thunderstore.is_installed(namespace,name,target_vers):
            print(f"Importing {namespace}-{name} from Thunderstore...")
            thunderstore.import_from_url(f"https://thunderstore.io/c/lethal-company/p/{namespace}/{name}/",target_vers,app.updateProgressBar)
        else:
            print(f"{namespace}-{name}-{target_vers} is already installed, skipping...")
            app.updateProgressCount()
    elif command == "delete_mod":
        namespace = split_commnad[1]
        name = split_commnad[2]
        app.updateProgressDisplay(f"Removing {namespace}-{name}")
        thunderstore_ops.uninstall_package(f"{namespace}-{name}")
        app.updateProgressCount()
    elif command == "update_vers":

        app.updateProgressDisplay(f"Updating version data")

        install_version = open_json(pblc_vers)
        mod_database_local = get_mod_database()
        new_patch_head = split_commnad[1]

        if len(split_commnad) == 2:
            print("Updating patch version")
            
            mod_database_local["patch_version"] = new_patch_head

        elif len(split_commnad) == 3:
            print("Updating patch and main version")

            
            new_version = split_commnad[2]

            install_version["version"] = new_version
            install_version["beta_version"] = "0.0.0"
            install_version["beta_goal"] = "0.0.0"
            mod_database_local["patch_version"] = new_patch_head

            with open(pblc_vers, "w") as patch_updater:
                patch_updater.write(json.dumps(install_version))
        
        elif len(split_commnad) == 4:
            print("Updating beta version")

            beta_goal = split_commnad[2]
            beta_version = split_commnad[3]

            install_version["version"] = "0.0.0"
            install_version["beta_version"] = beta_version
            install_version["beta_goal"] = beta_goal
            mod_database_local["patch_version"] = "0.0.0"

            with open(pblc_vers, "w") as patch_updater:
                patch_updater.write(json.dumps(install_version))
            

        with open(moddb_file, "w") as patch_db_updater:
                patch_db_updater.write(json.dumps(mod_database_local,indent=4))
                print(f"Updated patch version to {new_patch_head}")
        
        app.updateProgressCount()
    elif command == "download_bepinex":
        app.updateProgressDisplay(f"Downloading BepInEx")
        thunderstore_ops.install_bepinex()
        app.updateProgressCount() 
    elif command == "clean_install":
        app.updateProgressDisplay(f"Cleaning old files")
        if os.path.exists(bepinex_path):
            shutil.rmtree(bepinex_path)
        os.makedirs(f"{bepinex_path}/plugins")

        with open(moddb_file, "w") as moddb_reset:
            moddb_reset.write(json.dumps({"installed_mods":{},"patch_version":"0.0.0"},indent=4))
        
        app.updateProgressCount()

def installRelease(version,update_type):
    if update_type == "beta":
        update_instructions = grab_update_instructions(version,True)['instructions']
    else:
        update_instructions = grab_update_instructions(version)['instructions']
    
    for command in update_instructions:
        decodeDownloadCommand(command,app.updateProgressBar)

def startUpdate(update_data,update_type):
    time.sleep(0.5)
    print("Beginning download...")

    print(f"\nUpdating modpack to version {update_data['version']}\n")

    installRelease(update_data['version'],update_type)

    patch_db = grab_patch_instructions()
    if patch_db == None: return
    cur_patch_ver = version_man.get_patch()

    if update_data['version'] in patch_db and update_type == "release":
        for patch in patch_db[update_data['version']][update_type]:
            if version.Version(patch) > version.Version(cur_patch_ver):
                    applyNewPatches(patch_db,update_type,update_data['version'])
    

    update_finished = CTkMessagebox(title="PBLC Update Manager",message="Succsessfully installed update!",sound=True,button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
    print("Update installed, app will relaunch shortly.")
    app.redrawPBLCUI()
    #relaunch_location = os.path.normpath(os.path.join(getCurrentPathLoc(),"PBLC Update Manager.exe"))
    #if os.path.exists(relaunch_location):
    #    app.destroy()
    #    subprocess.run(relaunch_location)
    #else:
    #    print("Couldn't run EXE")
    #    #app.after(1500,app.destroy)

def updateManager(github_api_manager):
    print("Beginning manager update download...")
    time.sleep(2)

    zip_link = github_api_manager['assets'][0]['browser_download_url']


    temp_download_folder = os.path.normpath(f"{current_file_loc}/download_cache")
    print(temp_download_folder)
    target_zip = f"{temp_download_folder}/latest_manager.zip"

    if os.path.exists(temp_download_folder):
        shutil.rmtree(temp_download_folder)
        os.mkdir(temp_download_folder)
    else:
        os.mkdir(temp_download_folder)

    request.urlretrieve(zip_link,target_zip,show_progress)

    print("Download finished, beginning extraction...")

    decompress_zip(target_zip,temp_download_folder)

    print("Finished extracting, installing now...")

    subprocess.Popen(["python",resource_path("updater.py")])
    sys.exit()

def downloadOverridePatch(gdlink,dropbox):

    if not os.path.exists(downloads_folder):
        os.mkdir(downloads_folder)

    zip_down_loc = f"{downloads_folder}/pblc_patch.zip"
    app.updateProgressDisplay(f"Downloading {gdlink}")
    gd_file = download_from_google_drive(gdlink,zip_down_loc,app.updateProgressBar)
    if gd_file == "too_many_requests":
        if str(dropbox).endswith("&dl=0"):
            dropbox = str(dropbox).replace("&dl=0","&dl=1")
        app.updateProgressDisplay(f"Downloading {dropbox}")
        downloadFromURL(dropbox,zip_down_loc,app.updateProgressBar)
        app.updateProgressCount()
    decompress_zip(zip_down_loc,LC_Path)
    shutil.rmtree(downloads_folder)

def applyNewPatches(patch_db,update_type,cur_version,bar=None):
    time.sleep(0.5)
    cur_patch_ver = version_man.get_patch()

    for patch in patch_db[cur_version][update_type]:
        if version.Version(patch) > version.Version(cur_patch_ver):
            print(f"\nApplying patches for {cur_version}\n")
            for command in patch_db[cur_version][update_type][patch]:
                decodeDownloadCommand(command,bar)
            cur_patch_ver = patch


    new_version = version_man.install_version(update_type)
    cur_patch = version_man.get_patch()

    patch_list = [x for x in patch_db[new_version][update_type]]
    final_patch = patch_list[len(patch_list)-1]

    if cur_patch == final_patch:
        pass
    else:
        applyNewPatches(patch_db,update_type,new_version)

def applyNewPatchesEntry(patch_db,update_type,cur_version,bar=None):
    applyNewPatches(patch_db,update_type,cur_version,bar)
    app.redrawPBLCUI()
    CTkMessagebox(title="PBLC Update Manager",message="Finished installing patches!",icon=PBLC_Icons.checkmark(True))

def checkForPatches(update_type,cur_version):
    cur_version = str(cur_version)
    patch_db = grab_patch_instructions()
    if patch_db == None: return
    cur_patch_ver = version_man.get_patch()

    if cur_version in patch_db:
        try:
            for patch in patch_db[cur_version][update_type]:
                if version.Version(patch) > version.Version(cur_patch_ver):
                    user_response = CTkMessagebox(title="PBLC Update Manager",message=f"New patches found for PBLC v{cur_version}, would you like to apply them?",option_1="No",option_2="Yes",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))

                    if user_response.get() == "Yes":
                        print("Starting initial patch download")
                        threading.Thread(target=lambda patch_db=patch_db, update_type=update_type,cur_version=cur_version:applyNewPatchesEntry(patch_db,update_type,cur_version),daemon=True).start()
                        return "install_started"
                    else:
                        return "user_declined"
        except KeyError:
            pass
        
        return "no_patches"
    else:
        return "no_patches"

def patchesPrompt(self,update_type,install_version,github_repo_json,auto=False):
    #Checking for patches
    print(f"Checking for patches on {install_version}...")
    patches = checkForPatches(update_type,install_version)
    if patches == "no_patches":
        return "no_updates"
    elif auto and patches == 'user_declined':
        return "user_declined"
    elif patches == "install_started":
        app.drawUpdateUI()
        instruction_len = cacheInstructionLen("patches",str(install_version))
        app.updateProgressMax(instruction_len)
        return "install_started"
    elif patches == "finished_installing":
        self.redrawScrollFrame()
        response = CTkMessagebox(title="PBLC Update Manager",message="Patches finished installing, you can start the game now.",sound=True,icon=PBLC_Icons.checkmark(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
        self.update_manager_version.configure(text=f"\n\nCurrently Running: PBLC Stable v{version_man.install_version('release')}")
        return "finished_installing"

def callUpdateThread(github_repo_json,update_type):
    threading.Thread(target=lambda update_data = github_repo_json[update_type], update_type = update_type: startUpdate(update_data,update_type),daemon=True).start()

def checkForUpdates(self,update_type):

    print("Checking for updates...")

    draw_update_ui = False
    skip_checks = False

    #installed_version, installed_beta_version, json_data_internal, performance_mode = get_current_version(False)
    installed_stable_version = version.Version(version_man.install_version("release"))
    installed_beta_version = version.Version(version_man.install_version("beta"))

    #fetching latest version
    github_repo_json = grab_version_db()
    if github_repo_json == None:
        return
    needs_reinstall = github_repo_json[update_type]['needs_reinstall']
    base_vers_req = version.Version(github_repo_json[update_type]['starting_version'])
    pblc_min_vers = version.Version(github_repo_json[update_type]['pblc_min'])
    latest_version = version.Version(github_repo_json[update_type]['version']) if update_type == "release" else version.Version(github_repo_json[update_type]['beta_version'])

    #checking min reqs
    if pblc_min_vers > version.Version(PBLC_Update_Manager_Version):
        outdated_launcher = CTkMessagebox(title="PBLC Update Manager",message=f"ERROR: Update your PBLC Update Manager and try again!",button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),icon=PBLC_Icons.uninstall(True))
        return

    #RELEASE
    if update_type == "release":

        if not needs_reinstall:

            if installed_stable_version >= base_vers_req:
                response = patchesPrompt(self,update_type,installed_stable_version,github_repo_json,True)
                if response == "user_declined" or response == "finished_installing" or response == "install_started":
                    return
                elif response == "no_updates":
                    response = CTkMessagebox(title="PBLC Update Manager",message="No new patches found, you are up to date! Would you like to reinstall?",option_2="Reinstall",option_1="No",icon=PBLC_Icons.refresh(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
                    if response.get() == "Reinstall":
                        draw_update_ui = True
                        skip_checks = True
                        version_man.set_patch("0.0.0")
                        callUpdateThread(github_repo_json,update_type)
                        #startUpdate(github_repo_json[update_type],update_type)
        
        if not skip_checks:

            if not os.path.exists(bepinex_path) or not os.path.exists(doorstop_path) or not os.path.exists(winhttp_path) or installed_stable_version == version.Version("0.0.0"):
                print("Vanilla or broken version found.")
                prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"Vanilla or broken version detected, would you like to install the latest mods?",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
                if prompt_answer.get() == "Yes":
                    draw_update_ui = True
                    callUpdateThread(github_repo_json,update_type)
                    #startUpdate(github_repo_json[update_type],update_type)
            elif installed_beta_version > version.Version("0.0.0"):
                print("Beta release detected, prompting switch...")
                prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"It looks like you're using a beta version of our modpack, would you like to switch back to the last stable release?",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
                if prompt_answer.get() == "Yes":
                    draw_update_ui = True
                    callUpdateThread(github_repo_json,update_type)

            elif installed_stable_version < latest_version:
                print("New Update Found.")
                prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"An update is available, would you like to install it?\n{installed_stable_version} < {latest_version}",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
                if prompt_answer.get() == "Yes":
                    draw_update_ui = True
                    callUpdateThread(github_repo_json,update_type)
            else:
                response = patchesPrompt(self,update_type,installed_stable_version,github_repo_json)
                if response == "no_updates":
                    response = CTkMessagebox(title="PBLC Update Manager",message="No new patches found, you are up to date! Would you like to reinstall?",option_2="Reinstall",option_1="No",icon=PBLC_Icons.refresh(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
                    if response.get() == "Reinstall":
                        draw_update_ui = True
                        skip_checks = True
                        version_man.set_patch("0.0.0")
                        callUpdateThread(github_repo_json,update_type)

                #print("No updates found.")
                #ctypes.windll.user32.MessageBoxW(0, "No updates available.", "PBLC Update Manager")
    
    

    #BETA
    else:

        if not os.path.exists(bepinex_path) or not os.path.exists(doorstop_path) or not os.path.exists(winhttp_path) or (installed_beta_version == version.Version("0.0.0") and installed_stable_version == version.Version("0.0.0")):
            print("Vanilla or broken version found.")
            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"Vanilla or broken version detected, would you like to install the latest beta mods?",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
            if prompt_answer.get() == "Yes":
                draw_update_ui = True
                callUpdateThread(github_repo_json,update_type)

        elif installed_stable_version > version.Version("0.0.0"):
            print("Stable release found, prompting switch...")
            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"It looks like you're on the stable release of our modpack, would you like to switch to the latest beta?",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
            if prompt_answer.get() == "Yes":
                draw_update_ui = True
                callUpdateThread(github_repo_json,update_type)

        elif installed_beta_version < latest_version:
            print("New Beta Found.")
            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"A new beta is available, would you like to install it?",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
            if prompt_answer.get() == "Yes":
                draw_update_ui = True
                callUpdateThread(github_repo_json,update_type)
        
        else:

            print("No updates found.")
            CTkMessagebox(title="PBLC Update Manager",message="No updates available.",icon=PBLC_Icons.checkmark(True))
            #ctypes.windll.user32.MessageBoxW(0, "No updates available.", "PBLC Update Manager")
    
    #Drawing Update UI

    if draw_update_ui:
        app.drawUpdateUI()

        instruction_len = cacheInstructionLen("full",github_repo_json[update_type]['version'],update_type)
        app.updateProgressMax(instruction_len)

def checkForUpdatesmanager():
    github_api_manager = json.loads(request.urlopen(github_repo_latest_release).read().decode())
    latest_manager = str(github_api_manager['tag_name']).replace(".","")
    current_manager = PBLC_Update_Manager_Version.replace(".","")

    if current_manager < latest_manager:
        print("Manager update found, prompting user.")
        
        prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"A new manager version has been found, would you like to update?",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
        if prompt_answer.get() == "Yes":
            updateManager(github_api_manager)
    else:
        prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"No new updates found",icon=PBLC_Icons.checkmark(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))

def performanceModSwitchEvent(toggle):
    hd_company = os.path.join(plugins_folder,"HDLethalCompany")

    hd_company_en = os.path.normpath(f"{hd_company}.dll")
    hd_company_dis = os.path.normpath(f"{hd_company_en}_disabled")
    
    if os.path.exists(hd_company_en) or os.path.exists(hd_company_dis):
        try:
            if toggle == "on":
                os.rename(hd_company_dis,hd_company_en)
            else:
                os.rename(hd_company_en,hd_company_dis)
        except FileNotFoundError:
            pass
    else:
        print("NO HD LETHAL COMPANY DLL FOUND")

def requestWebData(url):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0)"
    }
    req = request.Request(url,headers=headers)
    return req

def uninstallMods():
    if os.path.exists(bepinex_path):
        shutil.rmtree(bepinex_path)
    if os.path.exists(winhttp_path):
        os.remove(winhttp_path)
    if os.path.exists(doorstop_path):
        os.remove(doorstop_path)

    with open(moddb_file, "w") as moddb_reset:
        moddb_reset.write(json.dumps({"installed_mods":{},"patch_version":"0.0.0"},indent=4))
    
    with open(pblc_vers, "w") as pblc_reset:
        pblc_reset.write(json.dumps({"version": "0.0.0", "beta_version": "0.0.0", "beta_goal": "0.0.0", "performance_mode": "off"}))

def downloadFromURL(download_link,download_loc,bar=None):

        pack_req = requests.get(download_link,stream=True)
        
        total_size_in_bytes = int(pack_req.headers.get('content-length', 0))
        widgets = [progressbar.Percentage(), ' ', progressbar.Bar()]
        progress_bar = progressbar.ProgressBar(maxval=total_size_in_bytes, widgets=widgets).start()

        with open(download_loc,'wb') as dl_package:
            chunk_count = 0
            for chunk in pack_req.iter_content(chunk_size=1024):
                dl_package.write(chunk)
                progress_bar.update(dl_package.tell())
                chunk_count += len(chunk)
                if bar:
                    bar(chunk_count, total_size_in_bytes)  

class widgetAnimation():
    def animate_border(master,start_color,end_color,duration):
        border_anim = pyeaze.Animator(current_value=start_color,target_value=end_color,duration=duration,fps=60,easing='ease')
        for color in border_anim:
            master.configure(border_color=color)
    

class thunderstore():
    def package_from_url(url):
        package_url = url.replace("https://","").split("/")
        package_namespace = package_url[4]
        package_name = package_url[5]
        return package_namespace, package_name
    
    def extract_package_json(namespace,name,version=None):
        if version:
            package_api_url = f"https://thunderstore.io/api/experimental/package/{namespace}/{name}/{version}"
        else:
            package_api_url = f"https://thunderstore.io/api/experimental/package/{namespace}/{name}"

        try:
            package_json = json.loads(request.urlopen(requestWebData(package_api_url)).read().decode())
        except URLError:
            print("Connection terminated.")
            return None
        
        return package_json
    
    def compare_versions(thunderstore_version,local_version):
        if version.Version(thunderstore_version) > version.Version(local_version):
            return True
        else:
            return False
    
    def url_import_entry(url,custom_version = None, bar=None, extend_max = False):
        thunderstore.import_from_url(url,custom_version,bar,extend_max)
        app.redrawPBLCUI()

    def import_from_url(url, custom_version = None, bar=None, extend_max = False):
        time.sleep(0.2)
        url_div = url.split("/")
        valid_threshold = ["thunderstore.io","c","lethal-company"]
        
        if all(entry in url_div for entry in valid_threshold):
            namespace = url_div[6]
            name = url_div[7]

            url_commands = url.split("--")
            del url_commands[0]

            active_commands = {
                "noDep" : False
            }

            for command in url_commands:
                active_commands[command] = True

            

            url_package_data = thunderstore.extract_package_json(namespace,name)
            if url_package_data == None:
                return None
            
            dependencies = url_package_data['latest']['dependencies']
            date_updated = url_package_data['latest']['date_created'].split("T")[0]
            
            if not custom_version.strip():
                target_version = url_package_data['latest']['version_number']
            else:
                target_version = custom_version
            
            print(f"Using version {target_version}...")

            if bar:
                app.updateProgressDisplay(f"Downloading {namespace}-{name}")
                app.updateProgressIcon(namespace,name,target_version)

            dep_count = 0

            for entry in dependencies:
                if str(entry).startswith("BepInEx"):
                    del dependencies[dep_count]
                dep_count += 1

            mod_database_local = get_mod_database()
            mod_list = mod_database_local["installed_mods"]
            
            mod_list[f"{namespace}-{name}"] = {
                "name": name,
                "author": namespace,
                "version": target_version,
                "update_date": date_updated,
                "package_url": url,
                "has_updates": "",
                "dependencies": dependencies,
                "enabled": "true",
                "files" : []
            }

            sort_thing = {}
            
            for mod in mod_list:
                sort_thing[mod_list[mod]['name']] = mod
            
            mod_names = list(sort_thing.keys())

            sorted_mod_list = sorted(mod_names, key=lambda x: x.lower())

            sorted_mod_dict = {}
            for key in sorted_mod_list:
                sorted_mod_dict[sort_thing[key]] = mod_list[sort_thing[key]]


            
            mod_database_local["installed_mods"] = sorted_mod_dict

            

            with open(moddb_file, "w") as mod_installer:
                mod_installer.write(json.dumps(mod_database_local,indent=4))
            

            #DOWNLOADING MOD

            print(f"Downloading {namespace}-{name}-{target_version}...")

            thunderstore_ops.download_package(namespace,name,target_version,dependencies,bar,extend_max)

            #Dependencies

            if not active_commands["noDep"]:
                for req_mod in dependencies:

                    split_name = req_mod.split("-")

                    internal_name = f"{split_name[0]}-{split_name[1]}"

                    if internal_name not in get_mod_database()['installed_mods']:
                        thunderstore.import_from_url(f"https://thunderstore.io/c/lethal-company/p/{split_name[0]}/{split_name[1]}/","",app.updateProgressBar, extend_max=True)



        else:
            print(f"{url} is not a valid Thunderstore package link!")

    def check_for_updates_all(self):
        mod_database_local = get_mod_database()

        mods_updating = 0

        for mod in mod_database_local["installed_mods"]:

            mod_inf = mod_database_local["installed_mods"][mod]
            
            if not mod_inf['version'] == "devmode":

                print(f"Checking for updates on {mod}")

                current_version = mod_inf['version']

                thunderstore_data_req = thunderstore.extract_package_json(mod_inf['author'],mod_inf['name'])

                #TEMP CODE
                #cur_vers_data = thunderstore.extract_package_json(mod_inf['author'],mod_inf['name'],mod_inf['version'])
                #update_date = cur_vers_data['date_created'].split("T")[0]

                latest_version = thunderstore_data_req['latest']['version_number']
                dependencies = thunderstore_data_req['latest']['dependencies']
                

                dep_count = 0
                for entry in dependencies:
                    if str(entry).startswith("BepInEx"):
                        del dependencies[dep_count]
                    dep_count += 1

                mod_database_local["installed_mods"][mod]['dependencies'] = dependencies
                mod_database_local["installed_mods"][mod]['enabled'] = "true"

                #mod_database_local["installed_mods"][mod]['update_date'] = update_date

                if thunderstore.compare_versions(latest_version,current_version):
                    mod_database_local["installed_mods"][mod]['has_updates'] = latest_version
                    mods_updating += 1
                    print(f"Updates found for: {mod}")
                else:
                    print(f"No Updates: {mod}")
            else:
                continue
            
        

        with open(moddb_file, "w") as update_checker_all:
            update_checker_all.write(json.dumps(mod_database_local,indent=4))
        
        finish_message = CTkMessagebox(title="PBLC Update Manager",message=f"Finished checking for updates, {mods_updating} mod(s) have updates available!",option_1="Ok",icon=PBLC_Icons.info(True),sound=True,button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
        print(f"\n\nFinished checking for updates, {mods_updating} mod(s) have updates available!")

    def is_installed(namespace,name,version):
        mod_database_local = get_mod_database()["installed_mods"]

        if f"{namespace}-{name}" in mod_database_local:
            if mod_database_local[f"{namespace}-{name}"]['version'] == version:
                return True
        
        return False

class thunderstore_ops():
    def check_for_updates(url,mod,bar=None):
        namespace, name = thunderstore.package_from_url(url)
        package_json = thunderstore.extract_package_json(namespace,name)
        has_updates = thunderstore.compare_versions(package_json['latest']['version_number'],get_mod_database()["installed_mods"][mod]['version'])
        dependencies = package_json['latest']['dependencies']
        dep_count = 0
        for entry in dependencies:
            if str(entry).startswith("BepInEx"):
                del dependencies[dep_count]
            dep_count += 1

        if has_updates:

            print(f"Updates for {name} found")

            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"Updates found for {name}, do you want to update?",option_2="Update",option_3="Specific Version",option_1="Cancel",icon=PBLC_Icons.download(True),sound=True,button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
            
            if prompt_answer.get() == "Update": #Downloads latest version
                thunderstore_ops.call_download_thread(namespace,name,package_json['latest']['version_number'],dependencies,bar=bar)
            if prompt_answer.get() == "Specific Version":
                dialog = customtkinter.CTkInputDialog(text="Enter Version:", title="PBLC Update Manager").get_input()
                print(f"Selected version = {dialog}")
                thunderstore_ops.call_download_thread(namespace,name,dialog,dependencies,bar=bar)
        else:
            print(f"Running latest version of {name}")

            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"No new updates for {name}, would you like to reinstall it or downgrade?",option_3="Downgrade",option_2="Yes",option_1="No",icon=PBLC_Icons.checkmark(True),sound=True,button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))

            if prompt_answer.get() == "Yes":
                thunderstore_ops.call_download_thread(namespace,name,package_json['latest']['version_number'],dependencies,bar=bar)
            elif prompt_answer.get() == "Downgrade":
                dialog = customtkinter.CTkInputDialog(text="Enter Version:", title="PBLC Update Manager",button_fg_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover")).get_input()
                if not dialog == None:
                    print(f"Selected version = {dialog}")
                    thunderstore_ops.call_download_thread(namespace,name,dialog,dependencies,bar=bar)
    def call_download_thread(namespace,name,version,dependencies,bar=None,extend_max=False):
        threading.Thread(target=lambda namespace=namespace,name=name,version=version,dependencies=dependencies,bar=bar,extend_max=extend_max: 
                         thunderstore_ops.download_package_entry(namespace,name,version,dependencies,bar,extend_max),daemon=True).start()
        app.drawUpdateUI()

    def download_package_entry(namespace,name,version,dependencies,bar=None,extend_max=False):
        thunderstore_ops.download_package(namespace,name,version,dependencies,bar,extend_max)
        app.redrawPBLCUI("Mods")

    def download_package(namespace,name,version,dependencies,bar=None,extend_max=False):
        try:
            version_test = f"https://thunderstore.io/api/experimental/package/{namespace}/{name}/{version}/"
            vers_response = json.loads(request.urlopen(requestWebData(version_test)).read().decode())
        except HTTPError:
            print("Invalid version number, did you enter it correctly?")
            return
        
        if bar:
            app.updateProgressIcon(namespace,name,version)
            if extend_max:
                app.extendProgressMax()



        download_link = f"https://thunderstore.io/package/download/{namespace}/{name}/{version}/"
        zip_name = f"{namespace}-{name}-{version}.zip"
        download_loc = os.path.join(downloads_folder,zip_name)

        if not os.path.exists(downloads_folder):
            os.mkdir(downloads_folder)

        
        pack_req = requests.get(download_link,stream=True)
        
        total_size_in_bytes = int(pack_req.headers.get('content-length', 0))
        widgets = [progressbar.Percentage(), ' ', progressbar.Bar()]
        progress_bar = progressbar.ProgressBar(maxval=total_size_in_bytes, widgets=widgets).start()
        
        #print(progress_bar.percentage())

        with open(download_loc,'wb') as dl_package:
            chunk_count = 0
            for chunk in pack_req.iter_content(chunk_size=1024):
                current_progress = round(progress_bar.percentage())
                
                dl_package.write(chunk)
                progress_bar.update(dl_package.tell())
                chunk_count += len(chunk)
                if bar:
                    bar(chunk_count, total_size_in_bytes)
        
        if bar:
            app.updateProgressCount()
                    
        
        decompress_zip(download_loc,downloads_folder)

        thunderstore_ops.install_package(namespace,name,version,dependencies)
    
    #def update_progress_bar()
    

    def copy_icon(cur_path,full_name):
        
        install_path = os.path.join(getCurrentPathLoc(),"data","pkg",full_name)
        fin_path = os.path.join(install_path,"icon.png")

        if os.path.exists(install_path):
            shutil.rmtree(install_path)
            os.mkdir(install_path)
        
        icon_png = Image.open(cur_path)
        icon_png = icon_png.resize((256,256))
        icon_png = roundImageCorners(icon_png,35)
        icon_png = icon_png.convert("RGBA")
        icon_png.save(fin_path)
    
    def log_sub_files(rel_start,folder,pre_folder=None):

        pkg_files = []

        special_folders = ["plugins","core","patchers","MoreCompanyCosmetics","Bundles"]

        for file in os.listdir(folder):
            #if os.path.isfile()
            if file in special_folders:
                sub_folders = thunderstore_ops.log_sub_files(rel_start,f"{folder}\\{file}")
                for x in sub_folders:
                    pkg_files.append(x)
            else:
                if os.path.isfile(f"{folder}\\{file}"):
                    if not pre_folder:
                        pkg_files.append(os.path.relpath(f"{folder}\\{file}",rel_start))
                    else:
                        pkg_files.append(os.path.join(pre_folder,os.path.relpath(f"{folder}\\{file}",rel_start)))
                elif os.path.isdir(f"{folder}\\{file}"):
                    sub_folders = thunderstore_ops.log_sub_files(rel_start,f"{folder}\\{file}")
                    for x in sub_folders:
                        pkg_files.append(x)
        return pkg_files


    def install_package(namespace,name,version,dependencies):

        print(f"Installing {namespace}-{name}")

        files = os.listdir(downloads_folder)

        delete_list = ["CHANGELOG.md","LICENSE","manifest.json","README.md"]
        bepinex_list = ["plugins","config","core","patchers"]
        full_name = f"{namespace}-{name}"
        pkg_folder = f"{getCurrentPathLoc()}/data/pkg/{namespace}-{name}"
        pkg_files = []
        
        if not os.path.exists(pkg_folder):
            os.mkdir(pkg_folder)

        for file in files:
            
            file_path = os.path.join(downloads_folder,file)
            
            if file in delete_list:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    continue
            
            print(file)
            
            #Special Files
            if file == "BepInEx":
                for x in thunderstore_ops.log_sub_files(file_path,file_path):
                    pkg_files.append(x)
                shutil.copytree(file_path,bepinex_path,dirs_exist_ok=True)
            elif file in bepinex_list:
                for x in thunderstore_ops.log_sub_files(downloads_folder,file_path):
                    pkg_files.append(x)
                shutil.copytree(file_path,f"{bepinex_path}/{file}",dirs_exist_ok=True)
            elif file == "icon.png":
                thunderstore_ops.copy_icon(file_path,full_name)
            else:
                if os.path.isfile(file_path):
                    pkg_files.append(f"plugins\\{file}")
                    move_file(file_path,f"{bepinex_path}/plugins/{file}")
                elif os.path.isdir(file_path):
                    for x in thunderstore_ops.log_sub_files(downloads_folder,file_path,"plugins"):
                        pkg_files.append(x)
                    shutil.copytree(file_path,f"{bepinex_path}/plugins/{file}",dirs_exist_ok=True)
        
        for pkg_file in pkg_files:
            disable_loc = os.path.normpath(f"{bepinex_path}/{pkg_file}_disabled")
            if os.path.exists(disable_loc):
                if os.path.isfile(disable_loc):
                    os.remove(disable_loc)
                elif os.path.isdir(disable_loc):
                    shutil.rmtree(disable_loc)
        
        shutil.rmtree(downloads_folder)

        #Updating Mod Database

        mod_database_local = get_mod_database()

        package_db = mod_database_local['installed_mods'][f"{namespace}-{name}"]
        package_db['version'] = version
        package_db['files'] = pkg_files
        package_db['has_updates'] = ""
        package_db['dependencies'] = dependencies

        

        with open(moddb_file, "w") as package_updater:
            package_updater.write(json.dumps(mod_database_local,indent=4))


        print(f"Finished installing {namespace}-{name}.")
            
    def uninstall_package(package):
        print(f"Uninstalling {package}")
        mod_database_local = get_mod_database()
        try:
            files_remove = mod_database_local['installed_mods'][package]['files']
        except KeyError:
            return
        data_folder = os.path.join(getCurrentPathLoc(),"data","pkg",package)

        for file in files_remove:
            file_path = os.path.normpath(f"{bepinex_path}\\{file}")
            
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    os.remove(file_path)
                else:
                    shutil.rmtree(file_path)
            elif os.path.exists(file_path+"_disabled"):
                if os.path.isfile(file_path+"_disabled"):
                    os.remove(file_path+"_disabled")
                else:
                    shutil.rmtree(file_path+"_disabled")
        
        if os.path.exists(data_folder):
            shutil.rmtree(data_folder)
        
        del mod_database_local['installed_mods'][package]

        

        with open(moddb_file, "w") as mod_deleter:
            mod_deleter.write(json.dumps(mod_database_local,indent=4))

        print(f"{package} uninstalled.")

    def toggle_package(package):
        mod_database_local = get_mod_database()
        package_data = mod_database_local["installed_mods"][package]

        if package_data['enabled'] == "true":
            for file in package_data['files']:
                file_path = os.path.join(bepinex_path,file)
                if os.path.exists(file_path):
                    os.rename(file_path, file_path+"_disabled")
                else:
                    print(f"Unable to find {file}, skipping...")
            mod_database_local["installed_mods"][package]['enabled'] = "false"
        elif package_data['enabled'] == "false":
            for file in package_data['files']:
                file_path = os.path.join(bepinex_path,file)
                if os.path.exists(file_path+"_disabled"):
                    os.rename(file_path+"_disabled",file_path)
                else:
                    print(f"Unable to find {file}, skipping...")
            mod_database_local["installed_mods"][package]['enabled'] = "true"
        
        

        with open(moddb_file, "w") as moddb_toggle:
            moddb_toggle.write(json.dumps(mod_database_local,indent=4)) 

    def install_bepinex():

        print("Installing BepInEx...")
        if not os.path.exists(downloads_folder):
            os.mkdir(downloads_folder)
        
        bepinex_zip = f"{downloads_folder}/bepinex.zip"
        
        downloadFromURL("https://thunderstore.io/package/download/BepInEx/BepInExPack/5.4.2100/",bepinex_zip,app.updateProgressBar)
        decompress_zip(bepinex_zip,downloads_folder)

        bepinex_pack = os.path.normpath(f"{downloads_folder}/BepInExPack")

        for file in os.listdir(bepinex_pack):
            filepath = f"{bepinex_pack}/{file}"
            if file == "BepInEx":
                shutil.copytree(filepath,f"{LC_Path}/{file}",dirs_exist_ok=True)
            else:
                shutil.move(filepath,f"{LC_Path}/{file}")
        
        shutil.rmtree(downloads_folder)
        print("Installed BepInEx")

    #def delete_package():

class thunderstoreModVersionLabel(customtkinter.CTkLabel):
    def __init__(self,master,mod):
        customtkinter.CTkLabel.__init__(self,master,font=('IBM 3270',16))
        self.mod = mod
        self.load_text(self.mod)

    def load_text(self,mod):
        json_db = get_mod_database()
        mod_db = json_db["installed_mods"][mod]
        try:
            if not mod_db['has_updates']:
                self.configure(text=mod_db['version'])
            else:
                self.configure(text=f"{mod_db['version']}   <   {mod_db['has_updates']}")
            try:
                update_date = mod_db['update_date']
            except KeyError:
                update_date = "0000-00-00"
            tooltip_thing = CTkToolTip(self,message=update_date,delay=0)
        except:
            pass
    
    def refresh_version(self,mod):
        self.load_text(mod)

class thunderstoreModIcon(customtkinter.CTkLabel):
    def __init__(self,master,mod):
        customtkinter.CTkLabel.__init__(self,master,text="",)
        self.mod = mod
        self.load_image()
    
    def load_image(self):

        mod_icon_path = os.path.join(getCurrentPathLoc(),"data","pkg",self.mod,"icon.png")
        if not os.path.exists(mod_icon_path):
            mod_icon_path = f"{getCurrentPathLoc()}/assets/missing_icon.png"
        icon_png = customtkinter.CTkImage(Image.open(mod_icon_path),size=(90,90))
        self.configure(image=icon_png)
        try:
            dependencies = get_mod_database()['installed_mods'][self.mod]['dependencies']
            depend_stripped = []
            for item in dependencies:
                split_item = item.split("-")
                depend_stripped.append(f"{split_item[0]}-{split_item[1]}")

            depend_string = "\n".join(depend_stripped)

            if depend_string.strip():
                tooltip_thing = CTkToolTip(self,message=depend_string,delay=0)
        except KeyError:
            print(f"Unable to find dependencies for {self.mod}")
    
    def refresh_icon(self):
        self.load_image()

class thunderstoreModToggle(customtkinter.CTkSwitch):
    def __init__(self,master,mod,fg_color,progress_color,outline,outline_size):
        customtkinter.CTkSwitch.__init__(self,master,fg_color=fg_color,progress_color=progress_color,switch_width=60,switch_height=30,onvalue="true",offvalue="false",text="",command=lambda mod_in=mod: self.toggle_mod(mod_in),border_color=outline,border_width=outline_size)
        self.mod = mod
        self.load_toggle()
    
    def load_toggle(self):
        try:
            mod_database_local = get_mod_database()["installed_mods"][self.mod]['enabled']
        except KeyError:
            print(f"Unable to determine toggle value for {self.mod}")
            mod_database_local = "true"
        self.switch_var = customtkinter.StringVar(value=mod_database_local)
        self.configure(variable=self.switch_var)
    
    def refresh_toggle(self):
        self.load_toggle
    
    def toggle_mod(self,mod):
        thunderstore_ops.toggle_package(mod)

class thunderstoreModScrollFrame(customtkinter.CTkScrollableFrame):
    def __init__(self,master,fg_color,width,height,parent):
        scroll_text = "           Mod Name                                      Version                               Actions"
        super().__init__(master,label_text=scroll_text,label_anchor="w",label_font=('IBM 3270',16),fg_color=fg_color,width=width,height=height,corner_radius=5)
        self.grid_columnconfigure(0,weight=1)
        self.parent = parent
        self.draw_mods_list()
    
    def draw_mods_list(self):

        i = 0

        mod_database_local = get_mod_database()

        for mod in mod_database_local["installed_mods"]:
        
            moddb = mod_database_local["installed_mods"][mod]

            print(f"Loading {mod}...")
    
            self.mod_entry_frame = customtkinter.CTkFrame(self,fg_color=PBLC_Colors.frame("darker"),corner_radius=5)
            self.mod_entry_frame.grid_columnconfigure(0, weight=0,minsize=105)
            self.mod_entry_frame.grid_columnconfigure(1, weight=1,minsize=20)
            self.mod_entry_frame.grid_columnconfigure(2, weight=0,minsize=185)
            self.mod_entry_frame.grid_columnconfigure(3, weight=0,minsize=1)
            self.mod_entry_frame.grid_columnconfigure(4, weight=0,minsize=1)
            self.mod_entry_frame.grid_columnconfigure(5, weight=0,minsize=1)
            self.mod_entry_frame.grid_columnconfigure(6, weight=0,minsize=1)
            self.mod_entry_frame.grid(row=i,column=0,sticky="we",pady=3)
    
            #self.mod_icon_img = customtkinter.CTkImage(Image.open(self.mod_icon_path),size=(90,90))
            #self.mod_icon_lab = customtkinter.CTkLabel(self.mod_entry_frame,text="",image=self.mod_icon_img)
            self.mod_icon_lab = thunderstoreModIcon(self.mod_entry_frame,mod)
            self.mod_icon_lab.grid(row=i,column=0,pady=2,padx=2,sticky="w")
    
            self.mod_name_author = customtkinter.CTkLabel(self.mod_entry_frame,text=f"{moddb['name']}\nby {moddb['author']}",justify='left',font=('IBM 3270',16))
            self.mod_name_author.grid(row=i,column=1,pady=2,sticky="w")

            self.mod_version = thunderstoreModVersionLabel(self.mod_entry_frame,mod)
            #self.mod_version = customtkinter.CTkLabel(self.mod_entry_frame,text=moddb['version'],font=('IBM 3270',16))
            self.mod_version.grid(row=i,column=2,pady=2,sticky="w")

            self.mod_toggle_switch = thunderstoreModToggle(self.mod_entry_frame,mod,PBLC_Colors.button("disabled"),PBLC_Colors.button("main"),PBLC_Colors.button("outline"),PBLC_Colors.button("outline_size"))
            self.mod_toggle_switch.grid(row=i,column=3,pady=2,padx=2,sticky="e")
            if not dev_mode and moddb['version'] == "devmode":
                self.mod_toggle_switch.configure(state="disabled",fg_color=PBLC_Colors.button("disabled_dark"))
            self.mod_toggle_tooltip = CTkToolTip(self.mod_toggle_switch,message=f"Toggle the current mod.",delay=0.3)
    
            self.website_icon = customtkinter.CTkImage(PBLC_Icons.website(),size=(30,30))
            self.website_icon_lab = customtkinter.CTkButton(self.mod_entry_frame,text="",width=45,height=45,image=self.website_icon,fg_color=PBLC_Colors.button("main_dark"),hover_color=PBLC_Colors.button("hover_dark"),command= lambda link=moddb['package_url']: self.openThunderstorePage(link),border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
            self.website_icon_lab.grid(row=i,column=4,pady=2,padx=2,sticky="e")
            if moddb['version'] == "devmode":
                self.website_icon_lab.configure(state="disabled",fg_color=PBLC_Colors.button("disabled_dark"))
            self.mod_website_tooltip = CTkToolTip(self.website_icon_lab,message=f"Open this mod's thunderstore page.",delay=0.3)
    
            self.refresh_icon = customtkinter.CTkImage(PBLC_Icons.refresh(),size=(30,30))
            self.refresh_icon_lab = customtkinter.CTkButton(self.mod_entry_frame,text="",width=45,height=45,image=self.refresh_icon,fg_color=PBLC_Colors.button("main_dark"),hover_color=PBLC_Colors.button("hover_dark"),command= lambda url=moddb['package_url'], mod_in = mod, version_grid=self.mod_version, icon_grid=self.mod_icon_lab: self.refreshThunderstorePackage(url,mod_in,version_grid,icon_grid),border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
            self.refresh_icon_lab.grid(row=i,column=5,pady=2,padx=2,sticky="e")
            if moddb['version'] == "devmode":
                self.refresh_icon_lab.configure(state="disabled",fg_color=PBLC_Colors.button("disabled_dark"))
            self.mod_refresh_tooltip = CTkToolTip(self.refresh_icon_lab,message=f"Check this mod for updates.",delay=0.3)
    
            self.delete_icon = customtkinter.CTkImage(PBLC_Icons.trash_can(),size=(30,30))
            self.delete_icon_lab = customtkinter.CTkButton(self.mod_entry_frame,text="",width=45,height=45,image=self.delete_icon,fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command= lambda mod_in=mod, frame = self.mod_entry_frame: self.uninstallThunderstorePackage(mod_in,frame),border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
            self.delete_icon_lab.grid(row=i,column=6,pady=2,padx=2,sticky="e")
            if moddb['version'] == "devmode":
                self.delete_icon_lab.configure(state="disabled",fg_color=PBLC_Colors.button("disabled_dark"))
            #self.mod_delete_tooltip = CTkToolTip(self.delete_icon_lab,message=f"Uninstall this mod.",delay=0.3)
            
            i+=1
    
    def testing(self,mod):
        print(f"no way real {mod}")
    
    def uninstallThunderstorePackage(self,mod,frame):
        thunderstore_ops.uninstall_package(mod)
        frame.destroy()
        #parent.redrawScrollFrame()
    
    def openThunderstorePage(self,link):
        print(f"Opening Thunderstore page...")
        webbrowser.open_new(link)
    
    def refreshThunderstorePackage(self,url,mod,version_grid,icon_grid):
        thunderstore_ops.check_for_updates(url,mod,app.updateProgressBar)
        version_grid.refresh_version(mod)
        icon_grid.refresh_icon()

class configSettingScrollFrame(customtkinter.CTkScrollableFrame):
    def __init__(self,master,fg_color,height):
        super().__init__(master,fg_color=fg_color,height=height)
        self.grid_columnconfigure(0,weight=1)
        self.draw_settings_ui()
    
    def draw_settings_ui(self):
        settings_data = settingsMan.returnSettingsData()

        field_index = 0
        
        for field in settings_data:

            self.field_frame = customtkinter.CTkFrame(self,fg_color=PBLC_Colors.frame("main"),corner_radius=5)
            self.field_frame.grid(row=field_index,column=0,sticky='nsew',pady=4)
            self.field_frame.grid_columnconfigure(0,weight=1)

            field_index+=1

            self.test_label = customtkinter.CTkLabel(self.field_frame,text=f"{field.capitalize()}:",font=('IBM 3270',30))
            self.test_label.grid(row=0,column=0,sticky='w',padx=10,pady=5)

            entry_index = 1

            for entry in settings_data[field]:

                self.setting_details = customtkinter.CTkFrame(self.field_frame,fg_color="black",width=400,height=100)
                self.setting_details.grid(row=entry_index,column=0,pady=3,padx=3,sticky='we')
                self.setting_details.grid_columnconfigure(0,weight=1)

                proper_text = str(entry).split("_")
                proper_text = " ".join(proper_text)
                self.setting_name = customtkinter.CTkLabel(self.setting_details,text=f"{proper_text.capitalize()}:",font=('IBM 3270',17))
                self.setting_name.grid(row=0,column=0,sticky='w',padx=(30,10),pady=2)

                setting_type = settingsMan.readSettingsValue(field,entry,3)

                if setting_type == 'string':

                    self.setting_value = customtkinter.CTkEntry(self.setting_details,placeholder_text=settingsMan.readSettingsValue(field,entry),width=500,height=38)
                    self.setting_value.grid(row=0,column=1,sticky='w',pady=5,padx=(0,2))
                
                elif setting_type == 'bool':

                    self.setting_box_var = customtkinter.StringVar(value=settingsMan.readSettingsValue(field,entry))
                    self.setting_value = customtkinter.CTkCheckBox(self.setting_details,text="",variable=self.setting_box_var,onvalue="True",offvalue="False")
                    self.setting_value.grid(row=0,column=1,sticky='w')

                self.save_icon = customtkinter.CTkImage(PBLC_Icons.save(),size=(30,30))
                self.save_settings = customtkinter.CTkButton(self.setting_details,text="",width=10,image=self.save_icon,command=lambda entrya=self.setting_value,field_i=field,entry_i=entry:threading.Thread(target=lambda entrya=entrya,field_i=field_i,entry_i=entry_i:self.update_setting(entrya,field_i,entry_i)).start())
                self.save_settings.grid(row=0,column=2,sticky='w',pady=5,padx=10)

                if settingsMan.readSettingsValue(field,entry,2):

                    self.entry_description = customtkinter.CTkLabel(self.setting_details,text=settingsMan.readSettingsValue(field,entry,1),font=customtkinter.CTkFont("Segoe UI",size=15,slant='italic'),text_color=PBLC_Colors.text("gray"))
                    self.entry_description.grid(row=1,column=0,sticky='w',padx=(60,0),columnspan=2)

                    self.entry_default = customtkinter.CTkLabel(self.setting_details,text=f"Default = {settingsMan.readSettingsValue(field,entry,2)}",font=customtkinter.CTkFont("Segoe UI",size=15,slant='italic'),text_color=PBLC_Colors.text("gray"))
                    self.entry_default.grid(row=2,column=0,sticky='w',padx=(90,0),pady=7,columnspan=2)
                else:
                    self.entry_description = customtkinter.CTkLabel(self.setting_details,text=settingsMan.readSettingsValue(field,entry,1),font=customtkinter.CTkFont("Segoe UI",size=15,slant='italic'),text_color=PBLC_Colors.text("gray"))
                    self.entry_description.grid(row=1,column=0,sticky='w',padx=(60,0),pady=7,columnspan=2)

                entry_index +=1
    
    def update_setting(self,entry_value,field,entry):

        settingsMan.writeSettingsValue(field,entry,entry_value.get())
        try:
            entry_value.configure(placeholder_text=entry_value.get())
            entry_value.delete(0,len(entry_value.get()))
        except:
            pass

        app.focus_set()
        widgetAnimation.animate_border(entry_value,PBLC_Colors.button("green_confirm"),PBLC_Colors.button("neutral_outline"),0.15)
        


class PBLC_Colors():
    def button(selection):
        options = {
            "main" : "#C44438",
            "disabled" : "#4C221E",
            "hover" : "#89271E",
            "main_dark" : "#3F3F3F",
            "hover_dark" : "#2D2D2D",
            "disabled_dark" : "#1f1f1f",
            "warning" : "#fb4130",
            "outline": "#dd786f",
            "outline_size": 2,
            "neutral_outline": "#565b5e",
            "green_confirm": "#3eff48"
        }

        if not selection in options:
            return PBLC_Colors.invalid()

        return options[selection]
    
    def frame(selection):
        options = {
            "main" : "#191919",
            "darker": "#0C0C0C",
            "update_ui": "#1a1a1a"
        }

        if not selection in options:
            return PBLC_Colors.invalid()

        return options[selection]
    
    def text(selection):
        options = {
            "gray": "#5c5c5c"
        }

        if not selection in options:
            return PBLC_Colors.invalid()

        return options[selection]

    def invalid():
        return "#ff00ea"

#UI
class PBLCApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x580")
        self.title(f"PBLC Update Manager - {PBLC_Update_Manager_Version}")
        self.minsize(1000,580)
        #self.resizable(False,False)
        self.iconbitmap(resource_path("assets/pill_bottle.ico"))

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.drawPBLCUI()
    
    def drawPBLCUI(self,default_frame="Home"):

        installed_version_disp, installed_beta_version_disp, json_data_internal_disp, performance_mode_disp = get_current_version()
        installed_version, installed_beta_version, json_data_internal, performance_mode = get_current_version(True)

        if installed_version > 0:
            install_latest_stable_text = "Update Stable Mods"
            install_latest_beta_text = "Switch to Beta Mods"
        elif installed_beta_version > 0:
            install_latest_stable_text = "Switch to Stable Mods"
            install_latest_beta_text = "Update Beta Mods"
        else:
            install_latest_stable_text = "Install Stable Mods"
            install_latest_beta_text = "Install Beta Mods"

        

        #frame

        self.tabview = customtkinter.CTkTabview(self,segmented_button_selected_color=PBLC_Colors.button("main"),segmented_button_selected_hover_color=PBLC_Colors.button("hover"))
        self.tabview.grid(row=0, column=0,sticky='nsew')

        if isScriptFrozen:
            tabs = ["Home","Mods","Extras"]
        else:
            tabs = ["Home","Mods","Extras","Dev"]
            
        for tab in tabs:
            self.tabview.add(tab)
            self.tabview.tab(tab).grid_columnconfigure(0, weight=1)
        
        self.tabview.set(default_frame)

        # Home

        print("Loading homepage...")

        self.bg_image = customtkinter.CTkImage(Image.open(resource_path("assets/lethal_art.png")),
                                               size=(500, 500))
        self.bg_image_label = customtkinter.CTkLabel(self.tabview.tab("Home"), image=self.bg_image,text="")
        self.bg_image_label.grid(row=0, column=0,sticky="w",padx=(5,0))

        self.bg_image = customtkinter.CTkImage(Image.open(resource_path("assets/lethal_art.png")),
                                               size=(500, 500))
        self.bg_image_label = customtkinter.CTkLabel(self.tabview.tab("Extras"), image=self.bg_image,text="")
        self.bg_image_label.grid(row=0, column=0,sticky="w",padx=(5,0))

        self.main_frame = customtkinter.CTkFrame(self.tabview.tab("Home"), corner_radius=0, fg_color="transparent")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=1)

        

        self.lethal_install_border = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color=PBLC_Colors.frame("main"))
        self.lethal_install_border.grid_columnconfigure(0, weight=1)
        self.lethal_install_border.grid_columnconfigure(1, weight=1)
        self.lethal_install_border.grid(row=1, column=0)

        self.lci_label = customtkinter.CTkLabel(self.lethal_install_border,text="Lethal Company Install Location:",font=('IBM 3270',26))
        self.lci_label.grid(row=0, column=0,padx=15,pady=10)
        
        self.lethal_install_path = customtkinter.CTkLabel(self.lethal_install_border,text=LC_Path,font=('Segoe UI',13))
        self.lethal_install_path.grid(row=1, column=0,padx=15,pady=10)

        self.actions_border = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color=PBLC_Colors.frame("main"),bg_color="transparent",corner_radius=5)
        self.actions_border.grid_columnconfigure(0, weight=1)
        self.actions_border.grid(row=2, column=0,pady=10)

        self.download_button = customtkinter.CTkImage(PBLC_Icons.download(),size=(15,15))
        self.update_button_main = customtkinter.CTkButton(self.actions_border,image=self.download_button, text=install_latest_stable_text,font=('IBM 3270',16),fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.check_for_updates_main,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.update_button_main.grid(row=0, column=0, padx=10, pady=20)

        self.update_button_main_2 = customtkinter.CTkButton(self.actions_border,image=self.download_button, text=install_latest_beta_text,font=('IBM 3270',16),fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.check_for_updates_beta,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.update_button_main_2.grid(row=0, column=1, padx=10, pady=20)

        self.performance_frame = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color=PBLC_Colors.frame("main"),bg_color="transparent",corner_radius=5)
        self.performance_frame.grid_columnconfigure(0, weight=1)
        self.performance_frame.grid(row=3, column=0)

        self.performance_mode_var = customtkinter.StringVar(value=performance_mode)
        self.performance_switch = customtkinter.CTkSwitch(self.performance_frame, text="Low Quality Mode",variable=self.performance_mode_var, onvalue="on", offvalue="off",fg_color=PBLC_Colors.button("disabled"),progress_color=PBLC_Colors.button("main"), command=self.performance_switch_event,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.performance_switch.grid(row=0, column=0, padx=10, pady=20)
        #self.performance_switch.configure(state="disabled")

        if not installed_version > 0 and not installed_beta_version > 0:
            self.performance_switch.configure(state="disabled")
        

        newEmptyRow(self,2,10)
        newEmptyRow(self,3,30)

        self.update_manager = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color=PBLC_Colors.frame("main"))
        self.update_manager.grid_columnconfigure(0, weight=1)
        self.update_manager.grid(row=4, column=0)

        self.new_builds_img = customtkinter.CTkImage(PBLC_Icons.arrow_up_right(),size=(15,15))
        self.update_self_button = customtkinter.CTkButton(self.update_manager,image=self.new_builds_img, text="Check for new builds",font=('IBM 3270',16),fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.check_for_updates_manager,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.update_self_button.grid(row=0, column=0, padx=20, pady=20)

        

        if installed_version > 0:
            display_text = f"PBLC Stable v{installed_version_disp}"
        elif installed_beta_version > 0:
            display_text = f"PBLC Beta v{installed_beta_version_disp} | v{json_data_internal['beta_goal']}"
        else:
            display_text = f"Vanilla Lethal Company"

        newEmptyRow(self,5,5)
        self.update_manager_credits = customtkinter.CTkLabel(self.main_frame,text=f"Version: {PBLC_Update_Manager_Version}\n\nDeveloped by DarthLilo  |  Testing by ExoticBuilder",font=('IBM 3270',16))
        self.update_manager_credits.grid(row=6, column=0)
        self.update_manager_version = customtkinter.CTkLabel(self.main_frame,text=f"\n\nCurrently Running: {display_text}",font=('IBM 3270',15))
        self.update_manager_version.grid(row=8, column=0)


        #Extras

        print("Loading extras menu...")

        self.main_frame = customtkinter.CTkFrame(self.tabview.tab("Extras"), corner_radius=0, fg_color="transparent")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=1)

        self.mods_list_frame = customtkinter.CTkFrame(self.main_frame,fg_color=PBLC_Colors.frame("main"),bg_color="transparent",corner_radius=5)
        self.mods_list_frame.grid_columnconfigure(0, weight=1)
        self.mods_list_frame.grid(row=2, column=0)

        self.pblc_pack_name = customtkinter.CTkEntry(self.mods_list_frame,placeholder_text="PBLC Pack Name",width=298)
        self.pblc_pack_name.grid(row=0,column=0,padx=10)


        self.archive_img = customtkinter.CTkImage(PBLC_Icons.archive(),size=(15,15))
        self.pblc_pack_trigger = customtkinter.CTkButton(self.mods_list_frame,image=self.archive_img,text="Export Modpack",fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.export_modpack,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.pblc_pack_trigger.grid(row=0,column=1,pady=20,padx=10)

        self.patch_save_img = customtkinter.CTkImage(PBLC_Icons.save(),size=(15,15))
        self.create_patch_save = customtkinter.CTkButton(self.mods_list_frame,image=self.patch_save_img,text="Create Patch Save",fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.create_patch_point,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.create_patch_save.grid(row=1,column=0,pady=20,padx=10)

        self.checklist_img = customtkinter.CTkImage(PBLC_Icons.checklist(),size=(15,15))
        self.generate_patch_changes = customtkinter.CTkButton(self.mods_list_frame,image=self.checklist_img,text="Generate Changes",fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.gen_patch_change,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.generate_patch_changes.grid(row=1,column=1,pady=20,padx=10)

        self.uninstall_img = customtkinter.CTkImage(PBLC_Icons.uninstall(),size=(15,15))
        self.uninstall_mods = customtkinter.CTkButton(self.mods_list_frame,image=self.uninstall_img,text="Uninstall Mods",fg_color=PBLC_Colors.button("warning"),hover_color=PBLC_Colors.button("hover"),command=self.uninstall_everything,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.uninstall_mods.grid(row=2,column=0,columnspan=2,pady=20,padx=20)

        #Mods

        print("Loading mods tab...")

        self.main_frame = customtkinter.CTkFrame(self.tabview.tab("Mods"), corner_radius=0, fg_color="transparent")
        self.main_frame.grid_columnconfigure(0, weight=0)
        self.main_frame.grid_columnconfigure(1, weight=0)
        self.main_frame.grid(row=0, column=0)

        #self.fetch_mods = customtkinter.CTkButton(self.main_frame, text="Fetch Mods", command=self.fetchModData)
        #self.fetch_mods.grid(row=3, column=0)

        self.thunderstore_mod_frame = thunderstoreModScrollFrame(self.main_frame,fg_color=PBLC_Colors.frame("main"),width=960,height=450,parent=self)
        self.thunderstore_mod_frame.grid(row=2,column=0,sticky="nsew")

        self.url_import_frame = customtkinter.CTkFrame(self.main_frame)
        self.url_import_frame.grid(row=3,column=0)

        self.import_url_box = customtkinter.CTkEntry(self.url_import_frame,width=550,placeholder_text="Thunderstore Package URL")
        self.import_url_box.grid(row=1,column=0,padx=3)
        self.import_url_box.bind("<Return>",lambda mod_frame=self.thunderstore_mod_frame: self.import_thunderstore_url(mod_frame))

        self.import_url_vers_box = customtkinter.CTkEntry(self.url_import_frame,width=130,placeholder_text="Version (Optional)")
        self.import_url_vers_box.grid(row=1,column=1,padx=3)
        self.import_url_vers_box.bind("<Return>",lambda mod_frame=self.thunderstore_mod_frame: self.import_thunderstore_url(mod_frame))

        self.import_from_url = customtkinter.CTkButton(self.url_import_frame,text="Import",fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=lambda mod_frame = self.thunderstore_mod_frame: self.import_thunderstore_url(mod_frame),border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.import_from_url.grid(row=1,column=2,pady=6,padx=3)

        self.check_for_updatesall = customtkinter.CTkButton(self.url_import_frame,text="Scan for Updates",fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.check_for_updates_all,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.check_for_updatesall.grid(row=1,column=3,pady=6,padx=3)

        print(f"Welcome to PBLC {PBLC_Update_Manager_Version}, the launcher is still currently in alpha and could be unstable, report any bugs to DarthLilo!")

        # Dev Only

        #
        #
        # Program - -
        #
        # Version Database Location/Url|update | MODE -> ONLINE/LOCAL
        #
        #
        # Patches - -
        #
        # Create Patch Save | Generate Changes
        #
        #
        # Modpack - -
        #
        # Pack Name | Export Modpack
        #
        # Uninstall Mods
        #


        if not isScriptFrozen:
            self.main_frame = customtkinter.CTkFrame(self.tabview.tab("Dev"), corner_radius=0, fg_color="transparent")
            self.main_frame.grid_rowconfigure(0, weight=1)
            self.main_frame.grid_columnconfigure(0, weight=1)
            self.main_frame.grid(row=0,column=0,sticky="nsew")
            
            self.devresetbutton = customtkinter.CTkButton(self.main_frame,text="display update ui",command=self.drawUpdateUI)
            self.devresetbutton.grid(row=0,column=0)

            self.devtestbutton = customtkinter.CTkButton(self.main_frame,text="download test file",command=self.tempDevFunc)
            self.devtestbutton.grid(row=1,column=0)
    
            #self.config_frame = configSettingScrollFrame(self.main_frame,fg_color="transparent",height=500)
            #self.config_frame.grid(row=0,column=0,sticky="nsew")
    
    def drawUpdateUI(self):
        print("Destroying main UI")
        self.destroyPBLCUI()
        print("Drawing Update UI...")

        self.update_frame = customtkinter.CTkFrame(self,fg_color="black")
        self.update_frame.grid(row=0,column=0,sticky="nsew")
        self.update_frame.grid_columnconfigure(0,weight=1)
        self.update_frame.grid_rowconfigure(0,weight=1)
        self.update_frame.grid_rowconfigure(1,weight=1)

        self.current_download = customtkinter.CTkFrame(self.update_frame,fg_color=PBLC_Colors.frame("update_ui"),corner_radius=15)
        self.current_download.grid(row=0,column=0,sticky='nsew',padx=40,pady=(20,5))
        self.current_download.grid_rowconfigure(0,weight=1)
        self.current_download.grid_rowconfigure(1,weight=1)
        self.current_download.grid_rowconfigure(2,weight=1)
        self.current_download.grid_columnconfigure(0,weight=1)

        self.pblc_progress_icon = customtkinter.CTkImage(dark_image=PBLC_Icons.lethal_company(),size=(250,250))
        self.pblc_progress_icon_display = customtkinter.CTkLabel(self.current_download,text="",image=self.pblc_progress_icon)
        self.pblc_progress_icon_display.grid(row=0,column=0,sticky='nsew',pady=(30,15))

        self.pblc_progress_bar = customtkinter.CTkProgressBar(self.current_download,width=250,height=20)
        self.pblc_progress_bar.grid(row=1,column=0,pady=(15,5),padx=20)
        self.pblc_progress_bar.set(0)

        self.pblc_progress_value = customtkinter.CTkLabel(self.current_download,text="0%",font=('IBM 3270',26))
        self.pblc_progress_value.grid(row=2,column=0,pady=(5,15))

        self.current_download_data = customtkinter.CTkFrame(self.update_frame,fg_color=PBLC_Colors.frame("update_ui"),corner_radius=15)
        self.current_download_data.grid(row=1,column=0,sticky='nsew',padx=40,pady=(5,20))
        self.current_download_data.grid_rowconfigure(0,weight=1)
        self.current_download_data.grid_rowconfigure(1,weight=1)
        self.current_download_data.grid_columnconfigure(0,weight=1)

        self.pblc_progress_display = customtkinter.CTkLabel(self.current_download_data,text="Initializing Download",font=('IBM 3270',20))
        self.pblc_progress_display.grid(row=0,column=0,padx=20,pady=(15,5),sticky='nsew')

        self.pblc_progress_int = 0
        self.pblc_progress_max = 0
        self.pblc_progress_count = customtkinter.CTkLabel(self.current_download_data,text="0/0",font=('IBM 3270',20),width=294)
        self.pblc_progress_count.grid(row=1,column=0,pady=(5,15),sticky='nsew')
    
    def updateProgressBar(self,chunk_count,total):
        new_prog = round(chunk_count/total,2)
        if not app.pblc_progress_bar.get() == new_prog:
            app.pblc_progress_bar.set(new_prog)
            app.pblc_progress_value.configure(text=f"{round(new_prog*100)}%")
    
    def updateProgressCount(self):
        app.pblc_progress_int += 1
        app.pblc_progress_count.configure(text=f"{app.pblc_progress_int}/{app.pblc_progress_max}")
        app.pblc_progress_bar.set(0)
        app.pblc_progress_display.configure(text="Initializing Download")
        app.pblc_progress_value.configure(text="0%")
    
    def updateProgressMax(self,max):
        app.pblc_progress_max = max
        app.pblc_progress_count.configure(text=f"{app.pblc_progress_int}/{app.pblc_progress_max}")
    
    def extendProgressMax(self):
        app.pblc_progress_max += 1

    def updateProgressDisplay(self,message):
        app.pblc_progress_display.configure(text=message)

    def updateProgressIcon(self,namespace,name,version):
        target_url = f"https://gcdn.thunderstore.io/live/repository/icons/{namespace}-{name}-{version}.png"
        try:
            geticon = requests.get(target_url)
            fin_img = Image.open(BytesIO(geticon.content))
        except Exception:
            fin_img = PBLC_Icons.missing_icon()
            traceback.print_exc()
        app.pblc_progress_icon.configure(dark_image=fin_img)

    def destroyPBLCUI(self):
        self.tabview.destroy()
    
    def redrawPBLCUI(self,default_frame="Home"):
        app.update_frame.destroy()
        app.drawPBLCUI(default_frame=default_frame)
        
    
    def tempDevFunc(self):

        app.redrawPBLCUI()

        #downloadFromURL("https://www.dropbox.com/scl/fi/e4hf9193q9ku82aplcng3/test.zip?rlkey=vxtyrub1vi3wf2uhu326i0cg0&st=mvqf77z0&dl=1","C:\\Users\\darth\\Desktop\\downloads\\test.zip") 
    
    # download_bepinex | GDCODE
    # url_add_mod | NAMESPACE | NAME | VERSION
    # delete_mod | NAMESPACE | NAME

    def uninstall_everything(self):
        uninstallMods()
        self.redrawScrollFrame()
        self.update_manager_version.configure(text=f"\n\nCurrently Running: Vanilla Lethal Company")

    def gen_patch_change(self):
        patch_save = f"{current_file_loc}/data/patch_point.json"
        patch_changes = f"{current_file_loc}/data/patch_changes.json"
        if not os.path.exists(patch_save):
            print("ERROR: No patch save found!")
            return
        
        print("Generating changes...")
        
        patch_save_data = open_json(patch_save)["installed_mods"]
        mod_database_local = get_mod_database()["installed_mods"]

        new_changes = {
            "new":[]
        }

        for mod in mod_database_local:
            if mod in patch_save_data:
                if mod_database_local[mod]['version'] != patch_save_data[mod]['version']:
                    new_changes['new'].append(f"url_add_mod|{mod_database_local[mod]['author']}|{mod_database_local[mod]['name']}|{mod_database_local[mod]['version']}")
            else:
                new_changes['new'].append(f"url_add_mod|{mod_database_local[mod]['author']}|{mod_database_local[mod]['name']}|{mod_database_local[mod]['version']}")
        
        for mod in patch_save_data:
            if mod not in mod_database_local:
                new_changes['new'].append(f"delete_mod|{patch_save_data[mod]['author']}|{patch_save_data[mod]['name']}")
        
        with open(patch_changes, "w") as patch_change:
            patch_change.write(json.dumps(new_changes,indent=4))
        
        print(f"Finished generating changes, find them at {patch_changes}")


    def create_patch_point(self):
        prompt_answer = CTkMessagebox(title="PBLC Update Manager",message="Are you sure you would like to create a save point? This may override existing data!",option_2="Yes",option_1="No",button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
        if prompt_answer.get() == "Yes":
            print("Updating patch save")
            patch_save = f"{current_file_loc}/data/patch_point.json"
            shutil.copy(moddb_file,patch_save)
    
    def export_modpack(self):
        export_folder = os.path.normpath(f"{getCurrentPathLoc()}/exports")
        zip_file_loc = f"{export_folder}/{self.pblc_pack_name.get()}.zip"

        if not os.path.exists(export_folder):
            os.mkdir(export_folder)
        
        target_files = [doorstop_path,winhttp_path,moddb_file]

        result = compress_zip(zip_file_loc,target_files)
        if result == "CANCELLED":
            CTkMessagebox(title="PBLC Update Manager",message="Error creating modpack zip, make sure you have a working install of BepInEx!",icon=PBLC_Icons.info(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
            return
        compress_zip_dir(zip_file_loc,bepinex_path)
        compress_zip_dir(zip_file_loc,package_data_path)
        print(f"Finished compressing {self.pblc_pack_name.get()}.zip!")
        

    
    def import_thunderstore_url(self,mod_frame):
        threading.Thread(target=lambda imp_url = self.import_url_box.get(), imp_box_url = self.import_url_vers_box.get() :thunderstore.url_import_entry(imp_url,imp_box_url,app.updateProgressBar),daemon=True).start()
        self.drawUpdateUI()
        self.extendProgressMax()
        #self.import_url_box.delete(0,len(self.import_url_box.get()))
        #self.import_url_vers_box.delete(0,len(self.import_url_vers_box.get()))
        #self.redrawScrollFrame()
    
    def check_for_updates_all(self):
        thunderstore.check_for_updates_all(self)

        for child in self.thunderstore_mod_frame.winfo_children():
            for subchild in child.winfo_children():
                if isinstance(subchild,thunderstoreModVersionLabel):
                    subchild.refresh_version(subchild.mod)
    
    def redrawScrollFrame(self):

        print("Redrawing Scroll UI")
    
        self.thunderstore_mod_frame.destroy()

        self.thunderstore_mod_frame = thunderstoreModScrollFrame(self.main_frame,fg_color=PBLC_Colors.frame("main"),width=960,height=450,parent=self)
        self.thunderstore_mod_frame.grid(row=2,column=0)
    # click_methods
    def check_for_updates_main(self):
        checkForUpdates(self,"release")
    
    def check_for_updates_beta(self):
        checkForUpdates(self,"beta")
    
    def check_for_updates_manager(self):
        checkForUpdatesmanager()

    def performance_switch_event(self):
        toggle = self.performance_mode_var.get()
        try:
            current_version = open_json(pblc_vers)
        except:
            current_version = default_pblc_vers
        
        current_version['performance_mode'] = toggle
        
        with open(pblc_vers, "w") as pblc_vers_upd:
            pblc_vers_upd.write(json.dumps(current_version))

        print("switch toggled, current value:",toggle)
        performanceModSwitchEvent(toggle)

app = PBLCApp()
app.mainloop()