import json, os, winreg, vdf, shutil, zipfile,gdown, sys, customtkinter, pyglet, subprocess, webbrowser, requests, validators, threading, configobj, time, traceback, datetime, pywinstyles, hPyT, ctkextensions, queue
from PIL import Image,ImageDraw
from urllib import request
from urllib.error import HTTPError
from packaging import version
from CTkMessagebox import CTkMessagebox
from CTkToolTip import *
from io import BytesIO

PBLC_Update_Manager_Version = "0.3.3"

github_repo_latest_release = "https://api.github.com/repos/DarthLilo/PBLC-Update-Manager/releases/latest"
thunderstore_pkg_url = "https://thunderstore.io/c/lethal-company/p"
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



def check_for_process(process_name):
    logMan.new(f"Checking for {process_name}")
    cmd = 'tasklist /fi "imagename eq {}"'.format(process_name)
    try:
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        if process_name.lower() in output.lower():
            return True
        else:
            return False
    except Exception as e:
        logMan.new(traceback.format_exc(),'error')
        logMan.new(f"Error when performing process check",'error')
        return False

def is_lethal_running():
    if check_for_process("Lethal Company.exe"):
        warning_display = CTkMessagebox(title="PBLC Update Manager",message="Lethal Company is running, please close it and try again!",button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),icon=PBLC_Icons.info(True))
        logMan.new("Lethal Company is running, please close it and try again!",'warning')
        return True
    return False

def read_reg(ep, p = r"", k = ''):
    try:
        key = winreg.OpenKeyEx(ep, p)
        value = winreg.QueryValueEx(key,k)
        if key:
            winreg.CloseKey(key)
        return value[0]
    except Exception as e:
        return None

def open_json(path):
    with open(path, 'r') as json_opener:
        json_data = json_opener.read()
    json_data = json.loads(json_data)

    return json_data

def roundImageCorners(source_image, rad):
    logMan.new(f"Rounding image {source_image}")
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

def is_python_installed():
    try:
        result = subprocess.run(['python','--version'],capture_output=True,text=True)
        if result.returncode == 0:
            logMan.new(f"Python is installed running version {result.stdout.strip()}")
            return True
        else:
            logMan.new("Python is not installed",'error')
            return False
    except FileNotFoundError:
        logMan.new("Python is not installed",'error')
        return False

class timeMan():
    def now():
        return datetime.datetime.timestamp(datetime.datetime.now())
    def date_now():
        return datetime.datetime.now()
    def time_passed(start,fin):
        start_time = datetime.datetime.fromtimestamp(start)
        fin_time = datetime.datetime.fromtimestamp(fin)
        difference = fin_time-start_time
        difference = round(difference.total_seconds())

        hours, remainder = divmod(difference, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
        return formatted_time
    def seconds_passed(start,fin):
        start_time = datetime.datetime.fromtimestamp(start)
        fin_time = datetime.datetime.fromtimestamp(fin)
        difference = fin_time-start_time
        difference = round(difference.total_seconds())
        return difference
    def log_start_time():
        return str(datetime.datetime.now().strftime("%d-%m-%Y"))
    def log_entry_time():
        return str(datetime.datetime.now().strftime("%H:%M:%S"))

class settingsMan():
        
    settings_file_path = os.path.normpath(f"{getCurrentPathLoc()}/data/pblc_update_man.ini")

    def generate_settings():
        if not os.path.exists(settingsMan.settings_file_path):
            settingsMan.resetSettingsDefault()
    
    def settings_library(container="",value="",return_all=False,return_comments=False):
        settings_lib = {
            "paths" : {
            "version_database": {"value":"","description":"Determines where the program checks for updates. URL or a FILEPATH","default":"","type":"string"},
            "update_instructions" : {"value":"","description":"Folder location of version update files. DIRPATH","default":"","type":"string"},
            "patch_instructions": {"value":"","description":"Determines where the program checks for patches. URL or a FILEPATH","default":"","type":"string"},
            "lethal_company_path": {"value":"","description":"Location of your Lethal Company root folder. DIRPATH","default":"","type":"string"}
            },

            "program" : {
                "check_for_updates_automatically": {"value": True,"description":"Does the program check for updates automatically on startup and prompt the user?","default":True,"type":"bool"},
                "auto_update_interval": {"value":"daily","description":"The interval at which the program will check for updates? Not recommended to change as you might fall behind!","default":"daily","type":"dropdown","values":["hourly","daily","weekly","bi-weekly","monthly"]},
                "last_check_timestamp": {"value": 0,"description":"Internal storage value for when the program last checked for an update.","default":"","type":"hidden"},
                "currently_has_update": {"value":False,"description":"Flags the program to display the update indicator.","default":"","type":"hidden"},
                "show_beta_options": {"value":False,"description":"Will the user be able to see the beta options?","default":False,"type":"bool"},
                "enable_mods_menu": {"value": False,"description":"Will the program cache enabled mods on startup or ignore them?","default":"","type":"bool"},
                "current_patch":{"value":"0.0.0","description":"The current installed patch, don't change unless you know what you're doing!","default":"0.0.0","type":"string"}
            }
        }
        settings_lib_comments = {
            "paths": ["Path related settings, changing these may break the program!"],
            "program": ["","General settings related to the program."]
        }
        if return_all:
            return settings_lib
        elif return_comments:
            return settings_lib_comments
        elif container and not value:
            return settings_lib[container]
        elif container and value:
            return settings_lib[container][value]

    def resetSettingsDefault():

        #data folder
        if not os.path.exists(os.path.join(getCurrentPathLoc(),"data")):
            os.mkdir(os.path.join(getCurrentPathLoc(),"data"))

        config=configobj.ConfigObj()
        config.filename = settingsMan.settings_file_path
        config.initial_comment = ["PBLC Update Manager Configuration",""]
        

        #CONFIG WRITING
        settings_lib = settingsMan.settings_library(return_all=True)
        settings_comments = settingsMan.settings_library(return_comments=True)
        for container in settings_lib:
            config[container] = settings_lib[container]
            config.comments[container] = settings_comments[container]

        config.write()

        return

    def readSettingsValue(container,value,index=0):
        config = configobj.ConfigObj(settingsMan.settings_file_path)
        selections = ['value','description','default','type','values']
        try:
            data = config[container][value][selections[index]]
        except (KeyError,IndexError) as e:
            logMan.new(f"Unable to find {container}/{value}/{index}, defaulting to None",'warning')
            data = None
        return data

    def writeSettingsValue(container,value,new_value):

        config = configobj.ConfigObj(settingsMan.settings_file_path)

        if container not in config:
            config[container] = settingsMan.settings_library(container)
        
        if value not in config[container]:
            config[container][value] = settingsMan.settings_library(container,value)

        config[container][value]['value'] = new_value

        config.write()

    def returnSettingsData():
        return configobj.ConfigObj(settingsMan.settings_file_path)

settingsMan.generate_settings()

class logMan():
    logs_folder = os.path.join(getCurrentPathLoc(),"data","logs")
    current_log = None
    def start():

        if not os.path.exists(os.path.join(getCurrentPathLoc(),"data","logs")):
            os.mkdir(os.path.join(getCurrentPathLoc(),"data","logs"))

        #Getting log count
        log_count = 1
        for file in os.listdir(logMan.logs_folder):
            if file.startswith(timeMan.log_start_time()):
                log_count += 1
        #Creating new log file
        logMan.current_log = f"{logMan.logs_folder}/{timeMan.log_start_time()}-{log_count}.pblc_log"
        logMan.new("Initialized logging system","startup")
    
    def new(message,log_type='info'):
        """Log Types
            - startup
            - info
            - warning
            - error"""
        log_types = {
            "startup":"[STARTUP]",
            "info":"[INFO]",
            "warning":"[WARNING]",
            "error":"[ERROR]"
        }

        current_thread = threading.current_thread()
        thread_name = current_thread.name

        log_entry = f"[{timeMan.log_entry_time()}] {log_types[log_type]} [{thread_name}] {message}"

        with open(logMan.current_log,'a') as log_write:
            log_write.write(log_entry+"\n")
        
        print(log_entry)
        return

    def close():
        current_thread = threading.current_thread()
        thread_name = current_thread.name
        log_entry = f"[{timeMan.log_entry_time()}] [END] [{thread_name}] PBLC Update Manager - {PBLC_Update_Manager_Version} is closing!"
        with open(logMan.current_log,'a') as log_write:
            log_write.write(log_entry)
        return
        
logMan.start()

class modDatabase():

    folder_path = os.path.normpath(f"{getCurrentPathLoc()}/data/mod_database")

    def get(mod=None,detailed=False,silent=False):
        if mod:
            if str(mod).startswith("DarthLilo-Mod"):
                return {}
            
            try:
                return open_json(os.path.join(modDatabase.folder_path,mod,"mod.json"))
            
            except FileNotFoundError:
                if not silent:
                    logMan.new(f"{mod} data file could not be found!",'warning')
                return {}
            
            except Exception as e:
                logMan.new(traceback.format_exc(),'error')
                return None
        elif detailed:

            mod_database_detailed = {}
            installed_mods = os.listdir(modDatabase.folder_path)
            for mod in installed_mods:
                mod_database_detailed[mod] = modDatabase.get(mod)
                mod_database_detailed[mod]['bar'] = True
                mod_database_detailed[mod]['extend_max'] = False
                mod_database_detailed[mod]['popup'] = False
            return mod_database_detailed
        
        else:
            return os.listdir(modDatabase.folder_path)
    
    def icon(mod):
        return os.path.join(modDatabase.folder_path,mod,"icon.png")
    
    def create_folder(mod):
        if os.path.exists(os.path.join(modDatabase.folder_path,mod)):
            return
        os.mkdir(os.path.join(modDatabase.folder_path,mod))
    
    def write(mod,data):
        logMan.new(f"Writing new data to {mod}")
        indent_value = 4
        target_folder = os.path.join(modDatabase.folder_path,mod)
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)

        with open(os.path.join(target_folder,"mod.json"), "w") as mod_database_write:
            mod_database_write.write(json.dumps(data,indent=indent_value))
    
    def remove(mod):
        logMan.new(f"Deleted {mod} data folder")
        shutil.rmtree(os.path.join(modDatabase.folder_path,mod))
    
    def reset():
        logMan.new(f"Resetting mod database")
        shutil.rmtree(modDatabase.folder_path)
        os.mkdir(modDatabase.folder_path)

def locate_lethal_company():

    custom_lethal_path = settingsMan.readSettingsValue("paths","lethal_company_path")
    
    if custom_lethal_path and os.path.exists(custom_lethal_path):
        return custom_lethal_path
    else:
        logMan.new("Locating Lethal Company path")
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
                logMan.new(f"Located Lethal Company path: {lethal_path}")
                return lethal_path

def download_from_google_drive(source,destination,bar=None,popup=False):
    logMan.new(f"Beginning download of {source} from Google Drive")
    try:
        gdown.download(id=source,output=destination,quiet=True)
        if bar:
            app.updateProgressCount()
        return "finished"
    except gdown.exceptions.FileURLRetrievalError:
        logMan.new(f"Google Drive file {source} has too many requests, attempting Dropbox download!",'warning')
        return "too_many_requests"

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
isScriptFrozen = getattr(sys, "frozen", False)

# download_override | GDCODE | DROPBOX
# url_add_mod | NAMESPACE | NAME | VERSION
# delete_mod | NAMESPACE | NAME
# update_vers | PATCH_VERSION | VERSION
# download_bepinex
# clean_install

dev_mode = f"{current_file_loc}/data/pooworms"
if not os.path.exists(dev_mode):
    logMan.new(f"Developer mode disabled")
    dev_mode = None



def grab_version_db():
    
    default_version_db = "https://raw.githubusercontent.com/DarthLilo/PBLC-Update-Manager/master/version_db.json"
    local_version_db = settingsMan.readSettingsValue("paths","version_database")
    is_url = False
    if validators.url(local_version_db):
        is_url = True
    
    if local_version_db and local_version_db.strip(): #Custom Path
        try:
            if is_url:
                return json.loads(request.urlopen(local_version_db).read().decode())
            else:
                return open_json(local_version_db)
        except:
            logMan.new("Config specifies invalid version database!",'warning')
            return None
    else: #default
        return json.loads(request.urlopen(default_version_db).read().decode())

def grab_patch_instructions():
    default_patch_instruct = "https://raw.githubusercontent.com/DarthLilo/PBLC-Update-Manager/master/patch_instructions.json"
    local_patch_instruct = settingsMan.readSettingsValue("paths","patch_instructions")
    is_url = False
    if validators.url(local_patch_instruct):
        is_url = True
    if local_patch_instruct and local_patch_instruct.strip(): #Custom Path
        try:
            if is_url:
                return json.loads(request.urlopen(local_patch_instruct).read().decode())
            else:
                return open_json(local_patch_instruct)
        except:
            logMan.new("Config specifies invalid patch instructions!",'warning')
            return None
    else: #default
        return json.loads(request.urlopen(default_patch_instruct).read().decode())

def grab_update_instructions(version,beta=False):
    
    default_update_instructions = "https://raw.githubusercontent.com/DarthLilo/PBLC-Update-Manager/master/update_files"
    local_update_instructions = settingsMan.readSettingsValue("paths","update_instructions")
    is_url = False
    if validators.url(local_update_instructions):
        is_url = True
    
    if local_update_instructions and local_update_instructions.strip(): #Custom Path
        try:
            if is_url:
                return json.loads(request.urlopen(f"{local_update_instructions}/{version}.json").read().decode())
            else:
                return open_json(f"{local_update_instructions}/{version}.json") if not beta else open_json(f"{local_update_instructions}/{version}_beta.json")
        except:
            logMan.new("Config specifies invalid update instructions!",'warning')
            return None
    else: #default
        return json.loads(request.urlopen(f"{default_update_instructions}/{version}.json").read().decode())

def startupFunc():
    cur_folder = getCurrentPathLoc()

    #data folder
    if not os.path.exists(os.path.join(cur_folder,"data")):
        logMan.new("Creating data folder")
        os.mkdir(os.path.join(cur_folder,"data"))
    else:
        logMan.new("Located data folder")

    if not os.path.exists(os.path.join(getCurrentPathLoc(),"data","extra_patches")):
        logMan.new("Creating extra patches folder")
        os.mkdir(os.path.join(getCurrentPathLoc(),"data","extra_patches"))
    
    if not os.path.exists(plugins_folder):
        os.makedirs(plugins_folder)
    
    
    mod_pkg = os.path.join(cur_folder,"data","pkg")

    if not os.path.exists(modDatabase.folder_path):
        logMan.new("Creating mod database folder")
        os.mkdir(modDatabase.folder_path)
    else:
        logMan.new("Found mod database folder")
    
    if not os.path.exists(mod_pkg):
        os.mkdir(mod_pkg)

startupFunc()


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
    
    def inactive_thread(pathOnly=False):
        if pathOnly:
            return 'assets/inactive_thread.png'
        return Image.open('assets/inactive_thread.png')
    
    def file(pathOnly=False):
        if pathOnly:
            return 'assets/file.png'
        return Image.open('assets/file.png')
    
    def plus(pathOnly=False):
        if pathOnly:
            return 'assets/plus.png'
        return Image.open('assets/plus.png')  

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
        try:
            patch_version = settingsMan.readSettingsValue("program","current_patch")
            return patch_version
        except Exception as e:
            logMan.new(traceback.format_exc(),'error')
            return "0.0.0"
    
    def set_patch(patch):
        settingsMan.writeSettingsValue("program","current_patch",patch)

def decompress_zip(zip_file,destination):
    logMan.new(f"Unzipping {os.path.basename(zip_file)}")
    with zipfile.ZipFile(zip_file, 'r',zipfile.ZIP_DEFLATED) as zip_ref:
        zip_ref.extractall(destination)
    os.remove(zip_file)

def compress_zip(zip_file,files):
    with zipfile.ZipFile(zip_file,'w',zipfile.ZIP_DEFLATED) as zipf:
        try:
            for file_path in files:
                relative_path = os.path.basename(file_path)
                logMan.new(f"Compressing {relative_path}")
                zipf.write(file_path,arcname=relative_path)
        except:
            return "CANCELLED"

def compress_zip_dir(zip_file,dir_path):
    with zipfile.ZipFile(zip_file,'a',zipfile.ZIP_DEFLATED) as zipf:
        for folder, _, files in os.walk(dir_path):
            for file in files:
                absolute_path = os.path.join(folder, file)
                relative_path = os.path.relpath(absolute_path, os.path.dirname(dir_path))
                logMan.new(f"Compressing {relative_path}")
                zipf.write(absolute_path, arcname=relative_path)

def cacheInstructionLen(cache_type,target_version,update_type="release"):
    logMan.new("Caching instruction length")
    instruction_len = 0

    if update_type == "release":
        update_instructions = grab_update_instructions(target_version)
    else:
        update_instructions = grab_update_instructions(target_version,True)


    if "url_add_mod|DarthLilo|!Developer_Mode|devmode" in update_instructions['instructions']:
        del update_instructions['instructions'][update_instructions['instructions'].index("url_add_mod|DarthLilo|!Developer_Mode|devmode")]

    patch_instruct = grab_patch_instructions()
    current_patch = version_man.get_patch()

    if cache_type == "full":
        instruction_len += len(update_instructions['instructions'])
    
    #patch len

    if update_type == "release":
        if target_version in patch_instruct:
            for patch in patch_instruct[target_version]['release']:
                if version.Version(patch) > version.Version(current_patch):
                    if cache_type == "patches":
                        patch_instruction_len = 0
                        for instruction in patch_instruct[target_version]['release'][patch]:
                            if str(instruction).startswith("url_add_mod"):
                                patch_instruction_len += 1
                    else:
                        patch_instruction_len = len(patch_instruct[target_version]['release'][patch])
                    
                    logMan.new(f"Found {patch_instruction_len} instructions")
                    instruction_len += patch_instruction_len

        #recursive version checking
        for release in patch_instruct:
            if version.Version(release) > version.Version(target_version):
                additional_inst_len = cacheInstructionLen(cache_type,release)
                logMan.new(f"Found {additional_inst_len} instructions")
                instruction_len += additional_inst_len
                break
    
    logMan.new(f"Total instruction length is {instruction_len}")

    return instruction_len

def decodeDownloadCommand(input_command,bar=False,popup=False,record_deps=False,ignore_add_mods=True):
    split_commnad = str(input_command).split("|")
    logMan.new(f"Decoding command {input_command}")

    command=split_commnad[0]
    if command == "download_override":
        gdlink = split_commnad[1]
        dropbox = split_commnad[2]
        logMan.new("Downloading override file")
        downloadOverridePatch(gdlink,dropbox,False,False)
        if bar:
            app.updateProgressCount()
    elif command == "url_add_mod":
        namespace = split_commnad[1]
        name = split_commnad[2]
        target_vers = split_commnad[3]
        if not ignore_add_mods:
            
            if bar:
                app.updateDownloadStatus(f"Downloading {namespace}-{name}")
            if not thunderstore.is_installed(namespace,name,target_vers):
                logMan.new(f"Downloading {namespace}-{name}-{target_vers} from Thunderstore")
                thunderstore.import_from_url(namespace,name,target_vers,bar,popup=popup,record_deps=record_deps)
            else:
                logMan.new(f"{namespace}-{name}-{target_vers} is already installed, skipping")
                if bar:
                    app.updateProgressCount()
        
    elif command == "delete_mod":
        namespace = split_commnad[1]
        name = split_commnad[2]
        if bar:
            app.updateDownloadStatus(f"Removing {namespace}-{name}")
        thunderstore_ops.uninstall_package(f"{namespace}-{name}")
        if bar:
            app.updateProgressCount()
        else:
            try:
                app.thunderstore_mod_frame.removeModFrame(name,namespace)
            except:
                pass
    elif command == "update_vers":

        app.updateDownloadStatus(f"Updating version data")

        if not os.path.exists(pblc_vers):
            with open(pblc_vers, "w") as default_pblc:
                default_pblc.write(json.dumps(default_pblc_vers)) 

        install_version = open_json(pblc_vers)
        new_patch_head = split_commnad[1]

        if len(split_commnad) == 2:
            logMan.new(f"Updating patch version to {new_patch_head}")
            
            version_man.set_patch(new_patch_head)

        elif len(split_commnad) == 3:

            new_version = split_commnad[2]

            logMan.new(f"Updating main version to {new_version}")
            logMan.new(f"Updating patch version to {new_patch_head}")

            
            

            install_version["version"] = new_version
            install_version["beta_version"] = "0.0.0"
            install_version["beta_goal"] = "0.0.0"
            version_man.set_patch(new_patch_head)

            with open(pblc_vers, "w") as patch_updater:
                patch_updater.write(json.dumps(install_version))
        
        elif len(split_commnad) == 4:
            logMan.new(f"Updating beta version to {beta_version}")

            beta_goal = split_commnad[2]
            beta_version = split_commnad[3]

            install_version["version"] = "0.0.0"
            install_version["beta_version"] = beta_version
            install_version["beta_goal"] = beta_goal
            version_man.set_patch("0.0.0")

            with open(pblc_vers, "w") as patch_updater:
                patch_updater.write(json.dumps(install_version))

        if bar:
            app.updateProgressCount()
    elif command == "download_bepinex":
        if bar:
            app.updateDownloadStatus(f"Downloading BepInEx")
        thunderstore_ops.install_bepinex(bar=bar)
    elif command == "clean_install":
        app.updateDownloadStatus(f"Cleaning old files")
        if os.path.exists(bepinex_path):
            shutil.rmtree(bepinex_path)
        os.makedirs(f"{bepinex_path}/plugins")

        modDatabase.reset()
        if bar:
            app.updateProgressCount()

class updateSystems():
    update_data = None
    update_type = None

    def startUpdate(update_data,update_type):
        time.sleep(0.5)
        updateSystems.update_data = update_data
        updateSystems.update_type = update_type

        logMan.new(f"Updating modpack to version {update_data['version']}")

        full_queue = updateSystems.queueInstructions(grab_update_instructions(update_data['version'])['instructions'])
        updateSystems.installRelease(update_data['version'],update_type,full_queue)
        queueMan.queuePackages(full_queue)
        queueMan.execute()

    def installRelease(version,update_type,full_queue):
        if update_type == "beta":
            update_instructions = grab_update_instructions(version,True)['instructions']
        else:
            update_instructions = grab_update_instructions(version)['instructions']

        for command in update_instructions:
            decodeDownloadCommand(command,app.updateProgressBar)

    def queueInstructions(update_instructions):
        #update_instructions = grab_update_instructions(version)['instructions']
        downloadQueueMan.clear_queue()
        new_database = {}
        for instruction in update_instructions:
            split_command = instruction.split("|")
            command = split_command[0]
            if command == "url_add_mod":
                author = split_command[1]
                name = split_command[2]
                version_num = split_command[3]
                new_database[f"{author}-{name}"] = {"name":name,"author":author,"version":version_num,"bar":True,"extend_max":False,"popup":False}

        full_queue = downloadQueueMan.queue_packages(new_database,True,True)
        return full_queue
    
    def finishUpdate():
        update_data = updateSystems.update_data
        update_type = updateSystems.update_type

        patch_db = grab_patch_instructions()
        if patch_db == None: return
        cur_patch_ver = version_man.get_patch()

        if update_data['version'] in patch_db and update_type == "release":
            for patch in patch_db[update_data['version']][update_type]:
                if version.Version(patch) > version.Version(cur_patch_ver):
                        instructions_queue = updateSystems.queueInstructions(patch_db[update_data['version']][update_type][patch])
                        applyNewPatches(patch_db,update_type,update_data['version'],app.updateProgressBar)
                        queueMan.clearQueue()
                        queueMan.queuePackages(instructions_queue)
                        queueMan._execute(False)

        update_finished = CTkMessagebox(title="PBLC Update Manager",message=f"Succsessfully installed update!\nElapsed Time: {app.pblc_elapsed_time.cget('text')}",sound=True,button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),icon=PBLC_Icons.checkmark(True))
        logMan.new("Finished installing update")
        app.redrawPBLCUI()

def updateManager(github_api_manager):
    logMan.new("Updating PBLC Update Manager")
    time.sleep(2)

    zip_link = github_api_manager['assets'][0]['browser_download_url']


    temp_download_folder = os.path.normpath(f"{current_file_loc}/download_cache")
    target_zip = f"{temp_download_folder}/latest_manager.zip"

    if os.path.exists(temp_download_folder):
        shutil.rmtree(temp_download_folder)
        os.mkdir(temp_download_folder)
    else:
        os.mkdir(temp_download_folder)

    request.urlretrieve(zip_link,target_zip)

    logMan.new("Finished downloading, extracting files")

    decompress_zip(target_zip,temp_download_folder)

    logMan.new("Finished extracting, installing now!")

    settingsMan.writeSettingsValue("program","currently_has_update",False)

    subprocess.Popen(["python",resource_path("updater.py")])
    sys.exit()

def downloadOverridePatch(gdlink,dropbox,bar,popup):
    overrides_folder = os.path.join(downloads_folder,"overrides")
    if not os.path.exists(overrides_folder):
        os.makedirs(overrides_folder,exist_ok=True)

    zip_down_loc = f"{overrides_folder}/pblc_patch.zip"
    if bar:
        app.updateDownloadStatus(f"Downloading {gdlink}")
    elif popup:
        app.pblc_progress_bar_popup.update_label(f"Downloading {gdlink}")

    gd_file = download_from_google_drive(gdlink,zip_down_loc,bar,popup)
    if gd_file == "too_many_requests":

        if str(dropbox).endswith("&dl=0"):
            dropbox = str(dropbox).replace("&dl=0","&dl=1")
        if bar:
            app.updateDownloadStatus(f"Downloading {dropbox}")
        elif popup:
            app.pblc_progress_bar_popup.update_label(f"Downloading {dropbox}")

        downloadFromURL(dropbox,zip_down_loc,bar,popup)
    decompress_zip(zip_down_loc,LC_Path)
    shutil.rmtree(overrides_folder)
    

def applyNewPatches(patch_db,update_type,cur_version,bar=None):
    time.sleep(0.5)
    cur_patch_ver = version_man.get_patch()

    for patch in patch_db[cur_version][update_type]:
        if version.Version(patch) > version.Version(cur_patch_ver):
            logMan.new(f"Applying patch for {cur_version}")
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
    patches_queue = []
    for patch in patch_db[cur_version][update_type]:
        if version.Version(patch) > version.Version(version_man.get_patch()):
            patches_queue.append(patch)
    
    for patch in patches_queue:
        instructions_queue = updateSystems.queueInstructions(patch_db[cur_version][update_type][patch])
        applyNewPatches(patch_db,update_type,cur_version,bar)
        queueMan.clearQueue()
        queueMan.queuePackages(instructions_queue)
        queueMan._execute(False)
    
    app.redrawPBLCUI()
    CTkMessagebox(title="PBLC Update Manager",message="Finished installing patches!",icon=PBLC_Icons.checkmark(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),sound=True)

def checkForPatches(update_type,cur_version):
    logMan.new(f"Requesting latest patches")
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
    logMan.new(f"Checking for new patches for version {install_version}")
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
        response = CTkMessagebox(title="PBLC Update Manager",message="Patches finished installing, you can start the game now.",sound=True,icon=PBLC_Icons.checkmark(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
        self.update_manager_version.configure(text=f"\n\nCurrently Running: PBLC Stable v{version_man.install_version('release')}")
        return "finished_installing"

def callUpdateThread(github_repo_json,update_type):
    threading.Thread(target=lambda update_data = github_repo_json[update_type], update_type = update_type: updateSystems.startUpdate(update_data,update_type),daemon=True).start()

def checkForUpdates(self,update_type):

    logMan.new("Checking for updates")

    draw_update_ui = False
    skip_checks = False

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
                logMan.new("Vanilla or broken version found, prompting install")
                prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"Would you like to install the mods? (May removed currently installed mods)",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),sound=True)
                if prompt_answer.get() == "Yes":
                    draw_update_ui = True
                    callUpdateThread(github_repo_json,update_type)
            elif installed_beta_version > version.Version("0.0.0"):
                logMan.new("Beta release found, prompting switch")
                prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"It looks like you're using a beta version of our modpack, would you like to switch back to the last stable release?",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),sound=True)
                if prompt_answer.get() == "Yes":
                    draw_update_ui = True
                    callUpdateThread(github_repo_json,update_type)

            elif installed_stable_version < latest_version:
                logMan.new("Update found!")
                prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"An update is available, would you like to install it?\n{installed_stable_version} < {latest_version}",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),sound=True)
                if prompt_answer.get() == "Yes":
                    draw_update_ui = True
                    callUpdateThread(github_repo_json,update_type)
            else:
                response = patchesPrompt(self,update_type,installed_stable_version,github_repo_json)
                if response == "no_updates":
                    logMan.new("No updates or patches found!")
                    response = CTkMessagebox(title="PBLC Update Manager",message="No new patches found, you are up to date! Would you like to reinstall?",option_2="Reinstall",option_1="No",icon=PBLC_Icons.refresh(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),sound=True)
                    if response.get() == "Reinstall":
                        draw_update_ui = True
                        skip_checks = True
                        version_man.set_patch("0.0.0")
                        callUpdateThread(github_repo_json,update_type)
    
    

    #BETA
    else:

        if not os.path.exists(bepinex_path) or not os.path.exists(doorstop_path) or not os.path.exists(winhttp_path) or (installed_beta_version == version.Version("0.0.0") and installed_stable_version == version.Version("0.0.0")):
            logMan.new("Vanilla or broken version found, prompting install")
            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"Would you like to install the mods? (May removed currently installed mods)",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),sound=True)
            if prompt_answer.get() == "Yes":
                draw_update_ui = True
                callUpdateThread(github_repo_json,update_type)

        elif installed_stable_version > version.Version("0.0.0"):
            logMan.new("Stable release found, prompting switch")
            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"It looks like you're on the stable release of our modpack, would you like to switch to the latest beta?",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),sound=True)
            if prompt_answer.get() == "Yes":
                draw_update_ui = True
                callUpdateThread(github_repo_json,update_type)

        elif installed_beta_version < latest_version:
            logMan.new("Beta update found!")
            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"A new beta is available, would you like to install it?",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),sound=True)
            if prompt_answer.get() == "Yes":
                draw_update_ui = True
                callUpdateThread(github_repo_json,update_type)
        
        else:

            logMan.new("No updates found!")
            CTkMessagebox(title="PBLC Update Manager",message="No updates available.",icon=PBLC_Icons.checkmark(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),sound=True)
    
    #Drawing Update UI

    if draw_update_ui:
        app.drawUpdateUI()

        instruction_len = cacheInstructionLen("full",github_repo_json[update_type]['version'],update_type)
        app.updateProgressMax(instruction_len)

def checkForUpdatesmanager(hidden=False):
    logMan.new("Checking for PBLC updates")
    github_api_manager = json.loads(request.urlopen(github_repo_latest_release).read().decode())
    latest_manager = str(github_api_manager['tag_name']).replace(".","")
    current_manager = PBLC_Update_Manager_Version.replace(".","")

    if hidden:
        if current_manager < latest_manager:
            logMan.new("Updates found, triggering button flash")
            settingsMan.writeSettingsValue("program","currently_has_update",True)
    else:

        if current_manager < latest_manager:
            logMan.new("Updates for mod manager found, prompting user!")

            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"A new manager version has been found, would you like to update?",option_2="Yes",option_1="No",icon=PBLC_Icons.download(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
            settingsMan.writeSettingsValue("program","currently_has_update",True)
            if prompt_answer.get() == "Yes":
                updateManager(github_api_manager)
        else:
            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"No new updates found",icon=PBLC_Icons.checkmark(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
            settingsMan.writeSettingsValue("program","currently_has_update",False)

def startupAutoUpdate():

    if not settingsMan.readSettingsValue("program","check_for_updates_automatically") == "True":
        return

    update_interval = settingsMan.readSettingsValue("program","auto_update_interval")
    last_time_var = settingsMan.readSettingsValue("program","last_check_timestamp")
    if last_time_var == None:
        last_time_var = 0
    time_since_last = int(timeMan.time_passed(float(last_time_var),timeMan.now()).split(":")[0])

    update_requirements = {
        "hourly": 1,
        "daily": 24,
        "weekly": 168,
        "bi-weekly": 336,
        "monthly": 744,
    }

    if not update_interval:
        update_interval = "daily"
        settingsMan.writeSettingsValue("program","auto_update_interval","daily")

    if time_since_last > update_requirements[update_interval]:
        settingsMan.writeSettingsValue("program","last_check_timestamp",timeMan.now())
        checkForUpdatesmanager(True)

    return

startupAutoUpdate()

def requestWebData(url):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0)"
    }
    req = request.Request(url,headers=headers)
    return req

def uninstallMods():
    logMan.new(f"Uninstalling all mods")
    if os.path.exists(bepinex_path):
        shutil.rmtree(bepinex_path)
    if os.path.exists(winhttp_path):
        os.remove(winhttp_path)
    if os.path.exists(doorstop_path):
        os.remove(doorstop_path)
    
    modDatabase.reset()
    
    with open(pblc_vers, "w") as pblc_reset:
        pblc_reset.write(json.dumps({"version": "0.0.0", "beta_version": "0.0.0", "beta_goal": "0.0.0", "performance_mode": "off"}))

def downloadFromURL(download_link,download_loc,bar=None,popup=False):
        
        logMan.new(f"Downloading from {download_link}")

        pack_req = requests.get(download_link,stream=True)
        
        total_size_in_bytes = int(pack_req.headers.get('content-length', 0))

        with open(download_loc,'wb') as dl_package:
            chunk_count = 0
            for chunk in pack_req.iter_content(chunk_size=1024):
                dl_package.write(chunk)
                chunk_count += len(chunk)
                if bar:
                    app.updateProgressBar(chunk_count,total_size_in_bytes,popup)


class widgetAnimation():
    def animate_border(master,start_color,end_color,duration):
        master.configure(border_color=start_color)
        time.sleep(duration)
        master.configure(border_color=end_color)
    
    def animate_fgcolor(master,start_color,end_color,duration):
        master.configure(fg_color=start_color)
        time.sleep(duration)
        master.configure(fg_color=end_color)
    
    def looping_border_flash(master,start_color,end_color,duration):
        try:
            widgetAnimation.animate_border(master,start_color,end_color,duration)
            time.sleep(1)
            widgetAnimation.looping_border_flash(master,start_color,end_color,duration)
        except:
            pass
    

class thunderstore():

    def package_from_url(url):
        logMan.new(f"Getting package data from URL")
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
            logMan.new(f"Making API call to thunderstore package {namespace}-{name}")
            package_json = json.loads(request.urlopen(requestWebData(package_api_url)).read().decode())
        except HTTPError as e:
            logMan.new(traceback.format_exc(),'error')
            logMan.new("Invalid package or version number!",'error')
            if e.code == 404:
                ctkextensions.CTkNotification(master=app, message="Invalid package or version number!", side="right_bottom")
                return "Invalid"
            if e.code == 520:
                time.sleep(5)
                return thunderstore.extract_package_json(namespace,name,version)
            if e.code == 429:
                logMan.new(f"Error retrieving package {namespace}-{name}-{version} from thunderstore, waiting and attempting again.",'error')
                logMan.new(traceback.format_exc(),'error')
                if app.update_screen_displayed:
                    app.updateDownloadStatus(f"Waiting for thunderstore response [{namespace}-{name}-{version}]")
                time.sleep(10)
                return thunderstore.extract_package_json(namespace,name,version)

        except Exception as e:
            logMan.new(traceback.format_exc(),'error')
            logMan.new("Connection terminated.",'error')
            return None
        
        return package_json
    
    def compare_versions(thunderstore_version,local_version):
        if version.Version(thunderstore_version) > version.Version(local_version):
            return True
        else:
            return False
    
    def batch_url_import(database,bar=False):
        downloadQueueMan.clear_queue()
        package_queue = downloadQueueMan.queue_packages(database,True,True)
        if bar:
            app.updateProgressMax(len(package_queue))
        queueMan.queuePackages(package_queue)
        queueMan.execute(False,simple_redraw=True)

    def url_import_entry(url,custom_version = None, package_queue = {}, bar=None, extend_max = False, popup = False):
        namespace, name = thunderstore.package_from_url(url)
        if not custom_version.strip():
            custom_version = package_queue[f"{namespace}-{name}"]['version']
        thunderstore.import_from_url(namespace,name,custom_version,package_queue[f"{namespace}-{name}"],bar,extend_max,popup,record_deps=False)
        del package_queue[f"{namespace}-{name}"]

        for package in package_queue:
            pkg_data = package_queue[package]
            thunderstore.import_from_url(pkg_data['namespace'],pkg_data['name'],pkg_data['version'],pkg_data,bar,extend_max,popup,record_deps=False)
        if popup:
            app.pblc_progress_bar_popup.close()
            if app.performance_switch.cget("state") == "disabled" and modDatabase.get("Sligili-HDLethalCompany",silent=True):
                app.performance_switch.configure(state="normal")
        app.pblc_app_is_busy = False

    def import_from_url(namespace, name, target_version, package_data, bar=False, extend_max = False, popup = False, record_deps = False, thread_index=0):
        time.sleep(0.2)
        dependencies = package_data['dependencies']
        date_updated = package_data['date_updated']

        modDatabase.create_folder(f"{namespace}-{name}")
        
        logMan.new(f"Installing version {target_version}")

        if bar:
            app.updateProgressDisplay(thread_index,f"Importing")
        if popup:
            app.pblc_progress_bar_popup.update_label(f"Downloading {namespace}-{name}")
            app.pblc_progress_bar_popup.update_message("0%")
            app.pblc_progress_bar_popup.update_progress(0)

        dep_count = 0

        for entry in dependencies:
            if str(entry).startswith("BepInEx"):
                del dependencies[dep_count]
            dep_count += 1
        
        mod_metadeta = {
            "name": name,
            "author": namespace,
            "version": target_version,
            "update_date": date_updated,
            "package_url": f"{thunderstore_pkg_url}/{namespace}/{name}",
            "has_updates": "",
            "dependencies": dependencies,
            "enabled": "true",
            "files" : []
        }
        modDatabase.write(f"{namespace}-{name}",mod_metadeta)
        

        #DOWNLOADING MOD

        logMan.new(f"Downloading {namespace}-{name}-{target_version}")

        if record_deps and extend_max:
            app.new_mods_list.append(f"url_add_mod|{namespace}|{name}|{target_version}")

        thunderstore_ops.download_package(namespace,name,target_version,dependencies,bar,extend_max,popup,thread_index)

    def check_for_updates_all(self):
        logMan.new(f"Checking all mods for updates, this might take a while")
        time.sleep(0.2)
        mod_database_local = modDatabase.get()

        mods_updating = 0

        app.updateProgressMax(len(mod_database_local),popup=True)

        for mod in mod_database_local:

            mod_inf = modDatabase.get(mod)
            
            if not mod_inf['version'] == "devmode":
                
                logMan.new(f"{mod} checking for updates")
                app.pblc_progress_bar_popup.update_label(f"Scanning {mod}")

                current_version = mod_inf['version']

                thunderstore_data_req = thunderstore.extract_package_json(mod_inf['author'],mod_inf['name'])

                latest_version = thunderstore_data_req['latest']['version_number']
                dependencies = thunderstore_data_req['latest']['dependencies']
                

                dep_count = 0
                for entry in dependencies:
                    if str(entry).startswith("BepInEx"):
                        del dependencies[dep_count]
                    dep_count += 1

                mod_inf['dependencies'] = dependencies
                mod_inf['enabled'] = "true"

                if thunderstore.compare_versions(latest_version,current_version):
                    mod_inf['has_updates'] = latest_version
                    mods_updating += 1
                    logMan.new(f"{mod} has updates: {latest_version}")
                else:
                    logMan.new(f"{mod} has no updates")
                app.updateProgressCount(True)
            else:
                continue
            modDatabase.write(mod,mod_inf)
        
        finish_message = CTkMessagebox(title="PBLC Update Manager",message=f"Finished checking for updates, {mods_updating} mod(s) have updates available!",option_1="Ok",icon=PBLC_Icons.info(True),sound=True,button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
        logMan.new(f"Finished checking mods for updates, {mods_updating} mod(s) have updates available!")

    def check_for_updates_all_entry(self):
        thunderstore.check_for_updates_all(self)

        app.pblc_progress_bar_popup.close()
        app.pblc_progress_int, app.pblc_progress_max = 0,0
        
        for child in self.thunderstore_mod_frame.winfo_children():
            for subchild in child.winfo_children():
                if isinstance(subchild,thunderstoreModLabel):
                    subchild.refresh_version(subchild.mod)

    def is_installed(namespace,name,version):
        mod_database_local = modDatabase.get()
        mod = f"{namespace}-{name}"

        if mod in mod_database_local:
            if modDatabase.get(mod)['version'] == version:
                return True
        
        return False

class thunderstore_ops():
    def check_for_updates(url,mod,bar=None,popup=False):
        namespace, name = thunderstore.package_from_url(url)
        package_json = thunderstore.extract_package_json(namespace,name)
        has_updates = thunderstore.compare_versions(package_json['latest']['version_number'],modDatabase.get(mod)['version'])

        if has_updates:
            
            logMan.new(f"Updates for {name} found")

            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"Updates found for {name}, do you want to update?",option_2="Update",option_3="Specific Version",option_1="Cancel",icon=PBLC_Icons.download(True),sound=True,button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
            
            if prompt_answer.get() == "Update": #Downloads latest version
                thunderstore_ops.call_download_thread(namespace,name,package_json['latest']['version_number'],bar=bar,popup=popup)
            if prompt_answer.get() == "Specific Version":
                dialog = customtkinter.CTkInputDialog(text="Enter Version:", title="PBLC Update Manager",button_fg_color=PBLC_Colors.button("main")).get_input()
                logMan.new(f"User selected version {dialog}")
                thunderstore_ops.call_download_thread(namespace,name,dialog,bar=bar,popup=popup)
        else:
            logMan.new(f"No updates found for {name}")

            prompt_answer = CTkMessagebox(title="PBLC Update Manager",message=f"No new updates for {name}, would you like to reinstall it or downgrade?",option_3="Downgrade",option_2="Yes",option_1="No",icon=PBLC_Icons.checkmark(True),sound=True,button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))

            if prompt_answer.get() == "Yes":
                thunderstore_ops.call_download_thread(namespace,name,package_json['latest']['version_number'],bar=bar,popup=popup)
            elif prompt_answer.get() == "Downgrade":
                dialog = customtkinter.CTkInputDialog(text="Enter Version:", title="PBLC Update Manager",button_fg_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover")).get_input()
                if not dialog == None:
                    logMan.new(f"User selected version {dialog}")
                    thunderstore_ops.call_download_thread(namespace,name,dialog,bar=bar,popup=popup)
    
    def call_download_thread(namespace,name,version,bar=False,extend_max=False,popup=False,ignore_popup_req=False):
        if not ignore_popup_req:
            if app.pblc_app_is_busy:
                logMan.new("User attempted to start multiple download threads at once, action cancelled!",'warning')
                return
        
        target_url = f"{thunderstore_pkg_url}/{namespace}/{name}/{version}" if version else f"{thunderstore_pkg_url}/{namespace}/{name}/"

        downloadQueueMan.clear_queue()

        if popup and not ignore_popup_req:
            app.pblc_progress_bar_popup = modDownloadPopup(app)

        package_queue = downloadQueueMan.queue_packages({f"{namespace}-{name}":{"name":name,"author":namespace,"version":version,"bar":bar,"extend_max":extend_max,"popup":popup}},True)
        if package_queue == "Invalid":
            app.pblc_progress_bar_popup.close()
            return
        threading.Thread(target=lambda imp_url = target_url, imp_box_url = version, package_queue = package_queue :thunderstore.url_import_entry(imp_url,imp_box_url,package_queue,popup=True),daemon=True).start()

    def download_package(namespace,name,version,dependencies,bar=False,extend_max=False,popup=False,thread_index=0):
        if bar:
            app.updateProgressDisplay(thread_index,f"Downloading")
            if extend_max:
                logMan.new(f"Extend progress max (download package) {namespace}-{name}-{version}")
                app.extendProgressMax()
        
        if popup:
            app.pblc_progress_bar_popup.update_label(f"Downloading {namespace}-{name}")
            app.pblc_progress_bar_popup.update_message("0%")
            app.pblc_progress_bar_popup.update_progress(0)


        download_link = f"https://thunderstore.io/package/download/{namespace}/{name}/{version}/"
        zip_name = f"{namespace}-{name}-{version}.zip"
        download_loc = os.path.join(downloads_folder,zip_name)

        if not os.path.exists(downloads_folder):
            os.mkdir(downloads_folder)

        
        pack_req = requests.get(download_link,stream=True)
        
        total_size_in_bytes = int(pack_req.headers.get('content-length', 0))

        with open(download_loc,'wb') as dl_package:
            chunk_count = 0
            for chunk in pack_req.iter_content(chunk_size=1024):
                dl_package.write(chunk)
                chunk_count += len(chunk)
                if bar:
                    app.mod_download_frame.threads[thread_index].progress(round(chunk_count/total_size_in_bytes,2))
                if popup:
                    app.updateProgressBar(chunk_count,total_size_in_bytes,True)
                    #app.pblc_progress_bar_popup.update_progress(round(chunk_count/total_size_in_bytes,2))
        
        if bar:
            app.updateProgressCount()

        local_downloads = f"{downloads_folder}/{namespace}-{name}"
        
        if not os.path.exists(local_downloads):
            os.makedirs(local_downloads)
        
        try:
            decompress_zip(download_loc,local_downloads)
            thunderstore_ops.install_package(namespace,name,version,dependencies,bar=bar,popup=popup)
        except zipfile.BadZipFile as e:
            logMan.new("Invalid zipfile, possibly due to download corruption? Requeuing and attempting again","error")
            logMan.new(traceback.format_exc(),'error')
            queueMan.queueSinglePackage({"name":name,"author":namespace,"version":version,"bar":bar,"extend_max":extend_max})
            shutil.rmtree(local_downloads)
            os.remove(download_loc)
            return  

    def copy_icon(cur_path,full_name):

        logMan.new(f"Copied icon {full_name}")
        
        install_path = os.path.join(modDatabase.folder_path,full_name)
        fin_path = os.path.join(install_path,"icon.png")

        if os.path.exists(fin_path):
            os.remove(fin_path)
        
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


    def install_package(namespace,name,version,dependencies,bar=None,popup=False):

        logMan.new(f"Installing {namespace}-{name}-{version}")

        local_download = f"{downloads_folder}/{namespace}-{name}"

        files = os.listdir(local_download)

        delete_list = ["CHANGELOG.md","LICENSE","LICENSE.txt","manifest.json","README.md"]
        bepinex_list = ["plugins","config","core","patchers"]
        full_name = f"{namespace}-{name}"
        pkg_folder = f"{getCurrentPathLoc()}/data/pkg/{namespace}-{name}"
        pkg_files = []
        
        if not os.path.exists(pkg_folder):
            os.mkdir(pkg_folder)

        for file in files:
            
            file_path = os.path.join(local_download,file)
            
            if file in delete_list:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    continue
            
            #Special Files
            if file.lower() == "bepinex":
                for x in thunderstore_ops.log_sub_files(file_path,file_path):
                    pkg_files.append(x)
                shutil.copytree(file_path,bepinex_path,dirs_exist_ok=True)
            elif file in bepinex_list:
                for x in thunderstore_ops.log_sub_files(local_download,file_path):
                    pkg_files.append(x)
                shutil.copytree(file_path,f"{bepinex_path}/{file}",dirs_exist_ok=True)
            elif file == "icon.png":
                thunderstore_ops.copy_icon(file_path,full_name)
            else:
                if os.path.isfile(file_path):
                    pkg_files.append(f"plugins\\{file}")
                    move_file(file_path,f"{bepinex_path}/plugins/{file}")
                elif os.path.isdir(file_path):
                    for x in thunderstore_ops.log_sub_files(local_download,file_path,"plugins"):
                        pkg_files.append(x)
                    shutil.copytree(file_path,f"{bepinex_path}/plugins/{file}",dirs_exist_ok=True)
        
        for pkg_file in pkg_files:
            disable_loc = os.path.normpath(f"{bepinex_path}/{pkg_file}_disabled")
            if os.path.exists(disable_loc):
                if os.path.isfile(disable_loc):
                    os.remove(disable_loc)
                elif os.path.isdir(disable_loc):
                    shutil.rmtree(disable_loc)

        #Updating Mod Database

        package_db = modDatabase.get(f"{namespace}-{name}")
        package_db['version'] = version
        package_db['files'] = pkg_files
        package_db['has_updates'] = ""
        package_db['dependencies'] = dependencies

        modDatabase.write(f"{namespace}-{name}",package_db)

        if popup:
            app.thunderstore_mod_frame.addNewModFrame(name,namespace,version,package_db['package_url'])

        shutil.rmtree(local_download)

        logMan.new(f"Finished installing {namespace}-{name}-{version}")
            
    def uninstall_package(package):
        logMan.new(f"Uninstalling {package}")
        try:
            files_remove = modDatabase.get(package)['files']
        except KeyError:
            return

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
        
        modDatabase.remove(package)

        logMan.new(f"{package} uninstalled")

    def toggle_package(package):
        package_data = modDatabase.get(package)

        logMan.new(f"Toggled {package}")

        if package_data['enabled'] == "true":
            for file in package_data['files']:
                file_path = os.path.join(bepinex_path,file)
                if os.path.exists(file_path):
                    os.rename(file_path, file_path+"_disabled")
                else:
                    logMan.new(f"Unable to find {file}, skipping",'warning')
            package_data['enabled'] = "false"
        elif package_data['enabled'] == "false":
            for file in package_data['files']:
                file_path = os.path.join(bepinex_path,file)
                if os.path.exists(file_path+"_disabled"):
                    os.rename(file_path+"_disabled",file_path)
                else:
                    logMan.new(f"Unable to find {file}, skipping",'warning')
            package_data['enabled'] = "true"
        
        
        modDatabase.write(package,package_data)

    def install_bepinex(bar=None):

        logMan.new("Installing BepInEx")
        if not os.path.exists(downloads_folder):
            os.mkdir(downloads_folder)
        
        bepinex_zip = f"{downloads_folder}/bepinex.zip"
        local_download = f"{downloads_folder}/bepinex"

        if not os.path.exists(local_download):
            os.mkdir(local_download)
        
        if bar:
            app.updateDownloadStatus("Downloading BepInEx")
        downloadFromURL("https://thunderstore.io/package/download/BepInEx/BepInExPack/5.4.2100/",bepinex_zip)
        decompress_zip(bepinex_zip,local_download)

        bepinex_pack = os.path.normpath(f"{local_download}/BepInExPack")

        for file in os.listdir(bepinex_pack):
            filepath = f"{bepinex_pack}/{file}"
            if file == "BepInEx":
                shutil.copytree(filepath,f"{LC_Path}/{file}",dirs_exist_ok=True)
            else:
                shutil.move(filepath,f"{LC_Path}/{file}")
        
        shutil.rmtree(local_download)
        logMan.new("BepInEx installed")
        if bar:
            app.updateProgressCount()

class queueMan():
    active_downloads = 0
    max_threads = 6 
    threads_status = {x:"open" for x in range(max_threads)}
    active_queue = queue.Queue()
    package_len = 0

    def return_open_thread():
        for thread in queueMan.threads_status:
            if queueMan.threads_status[thread] == "open":
                return thread
    
    def lock_thread(thread):
        queueMan.threads_status[thread] = "locked"
    
    def unlock_thread(thread):
        queueMan.threads_status[thread] = "open"

    def queuePackages(packages):
        '''Dictionary containing a bunch of packages to add to the queue, follows standard requirements'''
        queueMan.package_len = len(packages)
        for package in packages:
            queueMan.active_queue.put(packages[package])
    
    def queueSinglePackage(package):
        '''Queues a single package to the list containing required data:
        - name (Mod name)
        - author (Author/Namespace of the mod)
        - version (Targeted version of the mod)
        - bar (Is the progress screen visible)
        - extend_max (Should this progress increase the total count display)
        - popup (Whether the UI is using a popup progress bar)'''
        queueMan.package_len += 1
        queueMan.active_queue.put(package)
        logMan.new(f"Queued {package['name']}-{package['author']}-{package['version']}")
    
    def clearQueue():
        for tasks in range(queueMan.active_queue.qsize()):
            task = queueMan.active_queue.get()
            logMan.new(f"Removed {task} from queue")
    
    def _execute(finish_update=True,threads=max_threads,close_popup=False,simple_redraw=False):
        active_threads = []
        for i in range(min(threads,queueMan.package_len)):
            earliest_thread = queueMan.return_open_thread()
            queueMan.lock_thread(earliest_thread)
            thread = multithreadDownload(queueMan.active_queue,earliest_thread)
            thread.start()
            active_threads.append(thread)
        
        for i in range(threads):
            queueMan.active_queue.put(None)

        for thread in active_threads:
            logMan.new(f"{thread.name} joined into main thread")
            thread.join()
        
        logMan.new("All download threads have finished")
        if finish_update:
            updateSystems.finishUpdate()
        if close_popup:
            app.finish_patch_install()
        if simple_redraw:
            app.redrawPBLCUI()
  
    def execute(finish_update=True,threads=max_threads,close_popup=False,simple_redraw=False):
        threading.Thread(target=lambda finish_update = finish_update, threads = threads,close_popup = close_popup, simple_redraw=simple_redraw:queueMan._execute(finish_update,threads,close_popup,simple_redraw),daemon=True).start()
        logMan.new("Starting multithreaded download")
        if app.update_screen_displayed:
            app.updateDownloadStatus(f"Downloading Mods")

class downloadQueueMan():

    queue = {} #should look like this {"namespace":"","name":"","version":"","bar":True,"extend_max":False}

    def queue_packages(packages,start=False,update_count=False):
        '''Queues a database of packages to the list, each containing required data:
        - name (Mod name)
        - author (Author/Namespace of the mod)
        - version (Targeted version of the mod)
        - bar (Is the progress screen visible)
        - extend_max (Should this progress increase the total count display)'''
        for package in packages:
            if package in downloadQueueMan.queue:
                logMan.new(f"Package {package} was already queued, skipping")
                continue
            
            if str(package).startswith("DarthLilo-!Developer_Mode"):
                continue

            pkg = packages[package]
            package_type = "mod"
            if "type" in pkg:
                package_type = pkg['type']
            
            if package_type == "mod":

                if app.update_screen_displayed:
                    app.updateDownloadStatus(f"Caching {package}")
                
                namespace = pkg['namespace'] if 'namespace' in pkg else pkg['author']
                name = pkg['name']
                pkg_version = pkg['version']

                if (not start and update_count):
                    logMan.new(f"Extended progress max {namespace}-{name}-{pkg_version}")
                    app.extendProgressMax(update=True)

                package_data = thunderstore.extract_package_json(namespace, name, pkg_version)
                if package_data == "Invalid":
                    return "Invalid"
                if not pkg_version.strip():
                    package_data = package_data['latest']
                    pkg_version = package_data['version_number']
                dependencies = package_data['dependencies']
                date_updated = package_data['date_created'].split("T")[0]
                downloadQueueMan.queue[package] = {"namespace":namespace,"name":name,"version":pkg_version,"bar":pkg['bar'],"extend_max":False,"popup":pkg['popup'],"dependencies":dependencies,"date_updated":date_updated}


                dependencies_to_check = {}
                for dependency in dependencies:
                    if str(dependency).startswith("BepInEx-BepInExPack"):
                        continue
                    split_pkg = dependency.split("-")
                    if f"{split_pkg[0]}-{split_pkg[1]}" in packages:
                        logMan.new(f"Package {split_pkg[0]}-{split_pkg[1]} is already in update data, skipping to avoid requeue")
                        continue
                    if dependency in downloadQueueMan.queue:
                        logMan.new(f"Package {package} was already queued, skipping")
                        continue
                    
                    
                    dependency_check = modDatabase.get(f"{split_pkg[0]}-{split_pkg[1]}")
                    if dependency_check:    #0.16.1                             #0.15.1
                        if version.Version(dependency_check['version']) > version.Version(split_pkg[2]):
                            logMan.new(f"Package {f"{split_pkg[0]}-{split_pkg[1]}"} with version {dependency_check['version']} was found which is newer than what {package} requires. ({split_pkg[2]}) Keeping newer version")
                            continue
                        
                        elif version.Version(dependency_check['version']) == version.Version(split_pkg[2]):
                            logMan.new(f"Package {dependency} is already installed, skipping")
                            continue
                        
                        else:
                            logMan.new(f"Package {f"{split_pkg[0]}-{split_pkg[1]}"} is already installed but is running {dependency_check['version']} while {package} requires at least version {split_pkg[2]}, installing new version")

                    split_name = dependency.split("-")
                    dependency_namespace = split_name[0]
                    dependency_name = split_name[1]
                    dependency_version = split_name[2]

                    dependencies_to_check[f"{dependency_namespace}-{dependency_name}"] = {"namespace":dependency_namespace,"name":dependency_name,"version":dependency_version,"bar":pkg['bar'],"popup":pkg['popup']}

                downloadQueueMan.queue_packages(dependencies_to_check,update_count=update_count)
            else:
                downloadQueueMan.queue[package] = pkg

        if start:
            return downloadQueueMan.queue

    def clear_queue():
        downloadQueueMan.queue.clear()
        logMan.new("Cleared download queue")

class multithreadDownload(threading.Thread):
    def __init__(self, queue,thread_index):
        threading.Thread.__init__(self,daemon=True)
        self.queue = queue
        self.thread_index = thread_index
    
    def run(self):
        while True:
            package_data = self.queue.get()

            if package_data == None:
                self.queue.task_done()
                return
            
            author = package_data['author'] if 'author' in package_data else package_data['namespace']
            name = package_data['name']
            if package_data['bar'] == True:
                app.mod_download_frame.start_thread(self.thread_index,author,package_data['name'],package_data['version'])

            thunderstore.import_from_url(author,name,package_data['version'],package_data,package_data['bar'],package_data['extend_max'],thread_index=self.thread_index,popup=package_data['popup'])

            queueMan.unlock_thread(self.thread_index)
            if package_data['bar']:
                app.mod_download_frame.close_thread(self.thread_index)
            self.queue.task_done()

class thunderstoreModLabel(customtkinter.CTkFrame):
    def __init__(self,master,mod,name,author,override_vers=None):
        customtkinter.CTkFrame.__init__(self,master,fg_color="transparent")
        self.mod = mod
        self.name = name
        self.author = author
        self.override_vers = override_vers
        self.update_date = "0000-00-00"
        self.display_version = "0.0.0"
        self.render_mod_label(self.mod)
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        
    def render_mod_label(self,mod):
        self.mod_name_label = customtkinter.CTkLabel(self,text=self.name,justify="left",font=('IBM 3270',23))
        self.mod_name_label.grid(row=0,column=0,sticky='w')

        self.mod_version_label = customtkinter.CTkLabel(self,text=f"({self.display_version})",justify="left",font=('IBM 3270',14),text_color=PBLC_Colors.text("version_gray"))
        self.mod_version_label.grid(row=0,column=1,sticky='w',padx=10)
        self.refresh_version(mod)
        tooltip_thing = CTkToolTip(self.mod_version_label,message=self.update_date,delay=0)

        self.mod_author_label = customtkinter.CTkLabel(self,text=self.author,justify="left",font=('IBM 3270',17),text_color=PBLC_Colors.text("version_gray"))
        self.mod_author_label.grid(row=1,column=0,sticky='w')
        

    def determine_version(self,mod):
        mod_db = modDatabase.get(mod)

        if mod_db == None:
            if self.override_vers:
                self.display_version = self.override_vers
            else:
                self.display_version = "UNKNOWN"
            return
        
        try:
            if not mod_db['has_updates']:
                self.display_version =mod_db['version']
            else:
                self.display_version =f"{mod_db['version']}   <   {mod_db['has_updates']}"
            try:
                self.update_date = mod_db['update_date']
            except KeyError:
                self.update_date = "0000-00-00"
        except:
            pass
    
    def refresh_version(self,mod):
        self.determine_version(mod)
        self.mod_version_label.configure(text=f"({self.display_version})")

class thunderstoreModIcon(customtkinter.CTkLabel):
    def __init__(self,master,mod):
        customtkinter.CTkLabel.__init__(self,master,text="",)
        self.mod = mod
        self.load_image()
    
    def load_image(self):

        mod_icon_path = modDatabase.icon(self.mod)
        if not os.path.exists(mod_icon_path):
            logMan.new(f"Unable to find icon for {self.mod}, using missing icon",'warning')
            mod_icon_path = f"{getCurrentPathLoc()}/assets/missing_icon.png"
        icon_png = customtkinter.CTkImage(Image.open(mod_icon_path),size=(90,90))
        self.configure(image=icon_png)
        try:
            dependencies = modDatabase.get(self.mod)['dependencies']
            depend_stripped = []
            for item in dependencies:
                split_item = item.split("-")
                depend_stripped.append(f"{split_item[0]}-{split_item[1]}")

            depend_string = "\n".join(depend_stripped)

            if depend_string.strip():
                tooltip_thing = CTkToolTip(self,message=depend_string,delay=0)
        except (KeyError,FileNotFoundError):
            logMan.new(f"Unable to find dependencies for {self.mod}",'warning')

        except Exception as e:
            logMan.new(traceback.format_exc(),'error')
    
    def refresh_icon(self):
        self.load_image()

class thunderstoreModToggle(customtkinter.CTkSwitch):
    def __init__(self,master,mod,fg_color,progress_color,outline,outline_size):
        customtkinter.CTkSwitch.__init__(self,master,fg_color=fg_color,progress_color=progress_color,switch_width=60,switch_height=30,onvalue="true",offvalue="false",text="",command=lambda mod_in=mod: self.toggle_mod(mod_in),border_color=outline,border_width=outline_size)
        self.mod = mod
        self.load_toggle()
    
    def load_toggle(self):
        try:
            mod_database_local = modDatabase.get(self.mod)['enabled']
        except KeyError:
            logMan.new(f"Unable to determine toggle value for {self.mod}")
            mod_database_local = "true"
        self.switch_var = customtkinter.StringVar(value=mod_database_local)
        self.configure(variable=self.switch_var)
    
    def refresh_toggle(self):
        self.load_toggle
    
    def toggle_mod(self,mod):
        if is_lethal_running():
            return
        thunderstore_ops.toggle_package(mod)

class thunderstoreModScrollFrame(customtkinter.CTkScrollableFrame):
    def __init__(self,master,fg_color,width,height,parent, **kwargs):
        super().__init__(master,label_anchor="w",label_font=('IBM 3270',16),fg_color=fg_color,width=width,height=height,corner_radius=5,**kwargs)
        self.grid_columnconfigure(0,weight=1)
        self.parent = parent
        self.draw_mods_list()
    
    def draw_mods_list(self):

        i = 0

        mod_database_local = modDatabase.get()

        if settingsMan.readSettingsValue("program","enable_mods_menu") == "True":
            sorted_mod_list = sorted(mod_database_local,key=lambda x: x.split("-")[1].lower())

            for mod in sorted_mod_list:
                    moddb = modDatabase.get(mod)
                    if not moddb:
                        logMan.new(f"{mod} did not have a proper mod.json file, this could be due to a corrupted download or an extra folder in the [./data/mod_database] folder!",'warning')
                        continue

                    logMan.new(f"Loading {mod} into mods UI")

                    self.addModFrame(i,moddb['name'],moddb['author'],moddb['version'],moddb['package_url'])
                    i+=1
        else:
            self.addModFrame(i,"Mod caching is disabled!","DarthLilo","0.0.0","https://github.com/DarthLilo/PBLC-Update-Manager",True,"Built-in")
    
    def return_frames_list(self):
        frame_refs = {}
        for frame in self.winfo_children():
            root_frame = frame.winfo_children()[1]
            frame_children = root_frame.winfo_children()
            mod_name = str(frame_children[0].cget("text"))
            mod_author = str(frame_children[2].cget("text"))
            frame_refs[f"{mod_name}-{mod_author}"] = {}
            frame_refs[f"{mod_name}-{mod_author}"]['frame'] = frame
            frame_refs[f"{mod_name}-{mod_author}"]['version'] = root_frame
        return frame_refs

    def addModFrame(self,row,name,author,version,package_url,disabled=False,override_vers=None):
        
        if version == "devmode":
            disabled=True

        mod = f"{author}-{name}"
        self.mod_entry_frame = customtkinter.CTkFrame(self,fg_color=PBLC_Colors.frame("darker"),corner_radius=5)
        self.mod_entry_frame.grid_columnconfigure(0, weight=0,minsize=1)
        self.mod_entry_frame.grid_columnconfigure(1, weight=0,minsize=1)
        self.mod_entry_frame.grid_columnconfigure(2, weight=1,minsize=1)
        self.mod_entry_frame.grid_columnconfigure(3, weight=0,minsize=1)
        self.mod_entry_frame.grid_columnconfigure(4, weight=0,minsize=1)
        self.mod_entry_frame.grid_columnconfigure(5, weight=0,minsize=1)
        self.mod_entry_frame.grid_columnconfigure(6, weight=0,minsize=1)
        self.mod_entry_frame.grid_rowconfigure(0)
        self.mod_entry_frame.grid(row=row,column=0,sticky="we",pady=3)
    
        self.mod_icon_lab = thunderstoreModIcon(self.mod_entry_frame,mod)
        self.mod_icon_lab.grid(row=0,column=0,pady=2,padx=(2,10),sticky="w")
    
        #self.mod_name_author = customtkinter.CTkLabel(self.mod_entry_frame,text=f"{name}\nby {author}",justify='left',font=('IBM 3270',16))
        #self.mod_name_author.grid(row=0,column=1,pady=2,sticky="w")

        self.mod_version = thunderstoreModLabel(self.mod_entry_frame,mod,name,author,override_vers)
        self.mod_version.grid(row=0,column=1,pady=2,padx=10)

        self.mod_toggle_switch = thunderstoreModToggle(self.mod_entry_frame,mod,PBLC_Colors.button("disabled"),PBLC_Colors.button("main"),PBLC_Colors.button("outline"),PBLC_Colors.button("outline_size"))
        self.mod_toggle_switch.grid(row=0,column=2,pady=2,padx=2,sticky="e")
        if (not dev_mode and disabled) or disabled:
            self.mod_toggle_switch.configure(state="disabled",fg_color=PBLC_Colors.button("disabled_dark"),progress_color=PBLC_Colors.button("disabled"))
        self.mod_toggle_tooltip = CTkToolTip(self.mod_toggle_switch,message=f"Toggle the current mod.",delay=0.3)
    
        self.website_icon = customtkinter.CTkImage(PBLC_Icons.website(),size=(30,30))
        self.website_icon_lab = customtkinter.CTkButton(self.mod_entry_frame,text="",width=45,height=45,image=self.website_icon,fg_color=PBLC_Colors.button("main_dark"),hover_color=PBLC_Colors.button("hover_dark"),command= lambda link=package_url: self.openThunderstorePage(link),border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.website_icon_lab.grid(row=0,column=3,pady=2,padx=2,sticky="e")
        if disabled:
            self.website_icon_lab.configure(state="disabled",fg_color=PBLC_Colors.button("disabled_dark"))
        self.mod_website_tooltip = CTkToolTip(self.website_icon_lab,message=f"Open this mod's thunderstore page.",delay=0.3)
    
        self.refresh_icon = customtkinter.CTkImage(PBLC_Icons.refresh(),size=(30,30))
        self.refresh_icon_lab = customtkinter.CTkButton(self.mod_entry_frame,text="",width=45,height=45,image=self.refresh_icon,fg_color=PBLC_Colors.button("main_dark"),hover_color=PBLC_Colors.button("hover_dark"),command= lambda url=package_url, mod_in = mod, version_grid=self.mod_version, icon_grid=self.mod_icon_lab: self.refreshThunderstorePackage(url,mod_in,version_grid,icon_grid),border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.refresh_icon_lab.grid(row=0,column=4,pady=2,padx=2,sticky="e")
        if disabled:
            self.refresh_icon_lab.configure(state="disabled",fg_color=PBLC_Colors.button("disabled_dark"))
        self.mod_refresh_tooltip = CTkToolTip(self.refresh_icon_lab,message=f"Check this mod for updates.",delay=0.3)
    
        self.delete_icon = customtkinter.CTkImage(PBLC_Icons.trash_can(),size=(30,30))
        self.delete_icon_lab = customtkinter.CTkButton(self.mod_entry_frame,text="",width=45,height=45,image=self.delete_icon,fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command= lambda mod_in=mod, frame = self.mod_entry_frame: self.uninstallThunderstorePackage(mod_in,frame),border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.delete_icon_lab.grid(row=0,column=5,pady=2,padx=2,sticky="e")
        if disabled:
            self.delete_icon_lab.configure(state="disabled",fg_color=PBLC_Colors.button("disabled_dark"))
    
    def addNewModFrame(self,new_name,new_author,new_version,new_url):

        new_mod = f"{new_name}-{new_author}"

        frames = self.winfo_children()

        new_frames = []
        frame_refs = {}

        for frame in frames:
            root_children = frame.winfo_children()
            root_icon = root_children[0]
            root_frame = root_children[1]
            frame_children = root_frame.winfo_children()
            mod_name = str(frame_children[0].cget("text"))
            mod_author = str(frame_children[2].cget("text"))
            new_frames.append(f"{mod_name}-{mod_author}")
            frame_refs[f"{mod_name}-{mod_author}"] = {}
            frame_refs[f"{mod_name}-{mod_author}"]['frame'] = frame
            frame_refs[f"{mod_name}-{mod_author}"]['version'] = root_frame
            frame_refs[f"{mod_name}-{mod_author}"]['icon'] = root_icon

        if new_mod in new_frames:
            frame_refs[new_mod]['version'].refresh_version(f"{new_author}-{new_name}")
            frame_refs[new_mod]['icon'].refresh_icon()
            return
        add_mod_loader = ctkextensions.CTkLoader(app,opacity=0.4)
        
        new_frames.append(new_mod)
        sorted_frames_list = sorted(new_frames, key=lambda x: x.lower())
        
        for i in range(len(sorted_frames_list)):
            if sorted_frames_list[i] == new_mod:
                continue
            frame = frame_refs[sorted_frames_list[i]]['frame']
            frame.grid(row=i,column=0,sticky="we",pady=3)
        
        indices = [i for i, x in enumerate(sorted_frames_list) if x == new_mod]
        if indices:
            new_frame_index = max(indices)
        else:
            new_frame_index = sorted_frames_list.index(new_mod)

        self.addModFrame(new_frame_index,new_name,new_author,new_version,new_url)
        add_mod_loader.stop_loader()

    def removeModFrame(self,name,author):
        frames_list = self.return_frames_list()

        frames_list[f"{name}-{author}"]['frame'].destroy()

    def uninstallThunderstorePackage(self,mod,frame):
        if is_lethal_running():
            return
        thunderstore_ops.uninstall_package(mod)
        frame.destroy()
    
    def openThunderstorePage(self,link):
        logMan.new(f"Opening {link}")
        webbrowser.open_new(link)
    
    def refreshThunderstorePackage(self,url,mod,version_grid,icon_grid):
        if is_lethal_running():
            return
        thunderstore_ops.check_for_updates(url,mod,popup=True)
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

            self.settings_label = customtkinter.CTkLabel(self.field_frame,text=f"{field.capitalize()}:",font=('IBM 3270',30))
            self.settings_label.grid(row=0,column=0,sticky='w',padx=10,pady=5)

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
                    self.setting_value = customtkinter.CTkCheckBox(self.setting_details,text="",variable=self.setting_box_var,onvalue="True",offvalue="False",fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),border_color=PBLC_Colors.button("neutral_outline"))
                    self.setting_value.grid(row=0,column=1,sticky='w')
                
                elif setting_type == 'dropdown':
                    self.setting_value = customtkinter.CTkOptionMenu(self.setting_details,width=40,values=settingsMan.readSettingsValue(field,entry,4),fg_color=PBLC_Colors.button("main"),dropdown_hover_color=PBLC_Colors.button("hover"),button_color=PBLC_Colors.button("main"),hover=False,anchor='e')
                    self.setting_value.set(settingsMan.readSettingsValue(field,entry))
                    self.setting_value.grid(row=0,column=1,sticky='w',padx=(0,70))
                
                elif setting_type == 'hidden':
                    self.setting_value = customtkinter.CTkEntry(self.setting_details,width=200,height=38,placeholder_text=settingsMan.readSettingsValue(field,entry))
                    self.setting_value.grid(row=0,column=1,sticky='w',pady=5,padx=(0,2))
                    self.setting_value.configure(state='disabled')

                self.save_icon = customtkinter.CTkImage(PBLC_Icons.save(),size=(30,30))
                self.save_settings = customtkinter.CTkButton(self.setting_details,text="",width=10,fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),image=self.save_icon,border_width=PBLC_Colors.button("outline_size"),border_color=PBLC_Colors.button("outline"))
                self.save_settings.configure(command=lambda entrya=self.setting_value,field_i=field,entry_i=entry, setting_type=setting_type, self_button = self.save_settings:threading.Thread(target=lambda entrya=entrya,field_i=field_i,entry_i=entry_i, s_type = setting_type, s_button = self_button:self.update_setting(entrya,field_i,entry_i,s_type,s_button),daemon=True).start())
                if setting_type == 'hidden':
                    self.save_settings.configure(state='disabled',fg_color=PBLC_Colors.button("disabled"))
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
    
    def update_setting(self,entry_value,field,entry,s_type,self_button):

        settingsMan.writeSettingsValue(field,entry,entry_value.get())
        try:
            entry_value.configure(placeholder_text=entry_value.get())
            entry_value.delete(0,len(entry_value.get()))
        except:
            pass

        app.focus_set()

        if s_type == "string":
            widgetAnimation.animate_border(entry_value,PBLC_Colors.button("green_confirm"),PBLC_Colors.button("neutral_outline"),0.15)
        elif s_type == "bool":
            if entry_value.get() == "True":
                widgetAnimation.animate_fgcolor(entry_value,PBLC_Colors.button("green_confirm"),PBLC_Colors.button("main"),0.15)
            else:
                widgetAnimation.animate_border(entry_value,PBLC_Colors.button("green_confirm"),PBLC_Colors.button("neutral_outline"),0.15)
        elif s_type == "dropdown":
            widgetAnimation.animate_border(self_button,PBLC_Colors.button("green_confirm"),PBLC_Colors.button("outline"),0.15)

class modDownloadEntry(customtkinter.CTkFrame):
    def __init__(self,master,row,col,mod_title,status,thread_index,**kwargs):
        super().__init__(master,fg_color=PBLC_Colors.frame("darker"),height=110,corner_radius=5,**kwargs)
        self.grid_columnconfigure(0, weight=0,minsize=1)
        self.grid_columnconfigure(1, weight=1,minsize=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid(row=row,column=col,sticky="nsew",pady=10,padx=10)
        self.grid_propagate(False)
        
        self.thread_index = thread_index

        self.mod_icon_img = customtkinter.CTkImage(Image.open('assets/inactive_thread.png'),size=(90,90))
        self.mod_icon_lab = customtkinter.CTkLabel(self,text='',image=self.mod_icon_img)
        self.mod_icon_lab.grid(row=0,column=0,pady=10,padx=(10,10),sticky="w")

        self.mod_info_container = customtkinter.CTkFrame(self,fg_color='transparent')
        self.mod_info_container.grid_columnconfigure(0, weight=1,minsize=1)
        self.mod_info_container.grid_rowconfigure(0, weight=1,minsize=1)
        self.mod_info_container.grid_rowconfigure(1, weight=1,minsize=1)
        self.mod_info_container.grid_rowconfigure(2, weight=1,minsize=1)
        self.mod_info_container.grid_rowconfigure(3, weight=1,minsize=1)
        self.mod_info_container.grid(row=0,column=1,sticky='we')

        self.mod_title_display = customtkinter.CTkLabel(self.mod_info_container,text=mod_title,font=('IBM 3270',18))
        self.mod_title_display.grid(row=0,column=0,sticky='w')

        self.download_status_display = customtkinter.CTkLabel(self.mod_info_container,text=status,font=('IBM 3270',14),text_color=PBLC_Colors.text("version_gray"))
        self.download_status_display.grid(row=1,column=0,sticky='w')

        self.download_progress_display = customtkinter.CTkProgressBar(self.mod_info_container,progress_color=PBLC_Colors.button("main"))
        self.download_progress_display.grid(row=2,column=0,sticky='we',padx=(0,20))
        self.download_progress_display.set(0)

        self.download_progress_percent = customtkinter.CTkLabel(self.mod_info_container,text="0%",font=('IBM 3270',14),text_color=PBLC_Colors.text("version_gray"))
        self.download_progress_percent.grid(row=3,column=0,sticky='w')
    
    def name(self,new_value):
        self.mod_title_display.configure(text=new_value)
    
    def status(self,new_value):
        self.download_status_display.configure(text=new_value)
    
    def progress(self,new_value):
        if not self.download_progress_display.get() == new_value:
            self.download_progress_display.set(new_value)
            self.download_progress_percent.configure(text=f"{round(new_value*100)}%")
    
    def icon(self,new_image):
        self.mod_icon_lab.configure(image=new_image)

class modDownloadingScrollFrame(customtkinter.CTkFrame):
    def __init__(self,master,fg_color,width,height,parent, **kwargs):
        super().__init__(master,fg_color=fg_color,width=width,height=height,corner_radius=15,**kwargs)
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.parent = parent
        self.threads = []
        
        
        self.draw_mods_list()

    def draw_mods_list(self):
        self.threads.clear()

        logMan.new(f"Rendering threads UI")

        mod_thread_0 = modDownloadEntry(self,0,0,f"inactive_thread_{0}","Inactive",0)
        mod_thread_1 = modDownloadEntry(self,0,1,f"inactive_thread_{1}","Inactive",1)
        mod_thread_2 = modDownloadEntry(self,1,0,f"inactive_thread_{2}","Inactive",2)
        mod_thread_3 = modDownloadEntry(self,1,1,f"inactive_thread_{3}","Inactive",3)
        mod_thread_4 = modDownloadEntry(self,2,0,f"inactive_thread_{4}","Inactive",4)
        mod_thread_5 = modDownloadEntry(self,2,1,f"inactive_thread_{5}","Inactive",5)
        self.threads.append(mod_thread_0)
        self.threads.append(mod_thread_1)
        self.threads.append(mod_thread_2)
        self.threads.append(mod_thread_3)
        self.threads.append(mod_thread_4)
        self.threads.append(mod_thread_5)

    def rip_icon(self,namespace,name,version):
        target_url = f"https://gcdn.thunderstore.io/live/repository/icons/{namespace}-{name}-{version}.png"
        try:
            geticon = requests.get(target_url)
            fin_img = customtkinter.CTkImage(roundImageCorners(Image.open(BytesIO(geticon.content)),35),size=(90,90))
        except Exception:
            fin_img = customtkinter.CTkImage(PBLC_Icons.missing_icon(),size=(90,90))
            logMan.new("Error while drawing icon, check internet",'warning')
        return fin_img

    def start_thread(self,thread_index,namespace,name,version):

        self.threads[thread_index].icon(self.rip_icon(namespace,name,version))
        self.threads[thread_index].status("Starting Download")
        self.threads[thread_index].name(f"{namespace}-{name}")

        #self.update_icon(selected_frame,self.rip_icon(namespace,name,version))
        #self.update_status(selected_frame,"Starting Download")
        #self.update_name(selected_frame,f"{namespace}-{name}")
        return True

    def close_thread(self,thread_index):
        
        self.threads[thread_index].status("Inactive")
        self.threads[thread_index].progress(0)
        self.threads[thread_index].icon(customtkinter.CTkImage(PBLC_Icons.inactive_thread(),size=(90,90)))
        self.threads[thread_index].name(f"inactive_thread_{thread_index}")

        return True

class modDownloadPopup(ctkextensions.CTkProgressPopup):
    def __init__(self,master,popup_type="download",**kwargs):
        if popup_type == "download":
            title = "PBLC Update Manager"
            label = "Initializing Download"
            message = "0%"
        elif popup_type == "scan":
            title = "PBLC Update Manager"
            label = "Initializing Scan"
            message = "0/0"
        super().__init__(master,title,label,message,show_cancel_button=False,progress_color=PBLC_Colors.button("main"),**kwargs)
        app.pblc_progress_bar_storage = customtkinter.DoubleVar(value=0.0)
        app.pblc_app_is_busy = True
    
    def close(self):
        self.close_progress_popup()
        app.pblc_app_is_busy = False

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
            "gray": "#5c5c5c",
            "version_gray": "#bbb9ca"
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
        logMan.new(f"Drawing app")

        if not is_python_installed():
            logMan.new("Python isn't installed, please install it to continue!")
            user_response = CTkMessagebox(title="PBLC Update Manager",message="Python isn't installed, would you like to install it?",option_1="No",option_2="Yes",option_3="Open Webpage",button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),icon=PBLC_Icons.info(True))
            if user_response.get() == "Yes":
                subprocess.Popen(os.path.join(getCurrentPathLoc(),"lib","python_install.bat"))
            elif user_response.get() == "Open Webpage":
                webbrowser.open_new("https://www.python.org/downloads/release/python-3124/")
            
            sys.exit()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.start_time = None

        try:
            threading.Thread(target=self.drawPBLCUI,daemon=True).start()
        except Exception as e:
            logMan.new(traceback.format_exc(),'error')
        self.kill_clock = False

        self.pblc_app_is_busy = False
        self.pblc_progress_int = 0
        self.pblc_progress_max = 0
        self.update_screen_displayed = False
        self.pblc_progress_bar_storage = customtkinter.DoubleVar(value=0.0)

        self.new_mods_list = []
    
    def drawPBLCUI(self,default_frame="Home",loader=True):

        self.update_screen_displayed = False

        self.pblc_progress_int = 0
        self.pblc_progress_max = 0

        installed_version_disp, installed_beta_version_disp, json_data_internal_disp, performance_mode_disp = get_current_version()
        installed_version, installed_beta_version, json_data_internal, performance_mode = get_current_version(True)

        if installed_version > 0:
            install_latest_stable_text = "Update Mods"
            install_latest_beta_text = "Switch to Beta Mods"
        elif installed_beta_version > 0:
            install_latest_stable_text = "Switch to Stable Mods"
            install_latest_beta_text = "Update Beta Mods"
        else:
            install_latest_stable_text = "Install Mods"
            install_latest_beta_text = "Install Beta Mods"

        

        #frame

        self.tabview = customtkinter.CTkTabview(self,segmented_button_selected_color=PBLC_Colors.button("main"),segmented_button_selected_hover_color=PBLC_Colors.button("hover"))
        self.tabview.grid(row=0, column=0,sticky='nsew')

        if loader:
            self.loader_menu = ctkextensions.CTkLoader(self,opacity=1)

        if isScriptFrozen:
            tabs = ["Home","Mods","Extras","Config"]
        else:
            tabs = ["Home","Mods","Extras","Config","Dev"]
            
        for tab in tabs:
            self.tabview.add(tab)
            self.tabview.tab(tab).grid_columnconfigure(0, weight=1)
            self.tabview.tab(tab).grid_rowconfigure(0, weight=1)
        
        self.tabview.set(default_frame)

        # Home

        logMan.new(f"Drawing Home")

        self.background_frame = customtkinter.CTkFrame(self.tabview.tab("Home"),fg_color="black",bg_color="#2b2b2b",corner_radius=50)
        self.background_frame.grid(row=0,column=0,sticky='nsew')
        self.background_frame.grid_columnconfigure(0,weight=1)
        self.background_frame.grid_rowconfigure(0,weight=1)

        self.background_image = Image.open("assets/lethal_banner.png")
        self.bg_img_ctk = customtkinter.CTkImage(Image.open("assets/lethal_banner.png"),size=(988,532))
        self.background_image_label = customtkinter.CTkLabel(self.background_frame,image=self.bg_img_ctk,bg_color="#2b2b2b",text="")
        self.background_image_label.grid(row=0,column=0,sticky='nsew')

        self.main_frame = customtkinter.CTkFrame(self.background_frame,corner_radius=20,bg_color="#2b2b2a")
        self.main_frame.grid(row=0, column=0,sticky='ns',pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        for i in range(6):
            self.main_frame.grid_rowconfigure(i, weight=1)
        
        pywinstyles.set_opacity(self.main_frame,color="#2b2b2a")

        self.lethal_install_border = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color=PBLC_Colors.frame("main"),bg_color="transparent",corner_radius=15)
        self.lethal_install_border.grid_columnconfigure(0, weight=1)
        self.lethal_install_border.grid_columnconfigure(1, weight=1)
        self.lethal_install_border.grid(row=0, column=0,padx=20,pady=(12,0))

        self.lci_label = customtkinter.CTkLabel(self.lethal_install_border,text="Lethal Company Install Location:",font=('IBM 3270',26))
        self.lci_label.grid(row=0, column=0,padx=15,pady=(10,5))
        
        self.lethal_install_path = customtkinter.CTkLabel(self.lethal_install_border,text=LC_Path,font=('Segoe UI',13))
        self.lethal_install_path.grid(row=1, column=0,padx=15,pady=10)

        self.actions_border = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color=PBLC_Colors.frame("main"),bg_color="transparent",corner_radius=15)
        self.actions_border.grid_columnconfigure(0, weight=1)
        
        self.actions_border.grid(row=1, column=0,pady=10)

        self.download_button = customtkinter.CTkImage(PBLC_Icons.download(),size=(15,15))
        self.update_button_main = customtkinter.CTkButton(self.actions_border,image=self.download_button, text=install_latest_stable_text,font=('IBM 3270',16),fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.check_for_updates_main,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.update_button_main.grid(row=0, column=0, padx=20, pady=20)

        if settingsMan.readSettingsValue("program","show_beta_options") == "True":
            self.actions_border.grid_columnconfigure(1, weight=1)
            self.update_button_main_2 = customtkinter.CTkButton(self.actions_border,image=self.download_button, text=install_latest_beta_text,font=('IBM 3270',16),fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.check_for_updates_beta,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
            self.update_button_main_2.grid(row=0, column=1, padx=15, pady=20)

        self.performance_frame = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color=PBLC_Colors.frame("main"),bg_color="transparent",corner_radius=15)
        self.performance_frame.grid_columnconfigure(0, weight=1)
        self.performance_frame.grid(row=2, column=0)

        self.performance_mode_var = customtkinter.StringVar(value=performance_mode)
        self.performance_switch = customtkinter.CTkSwitch(self.performance_frame, text="Performance Mode",variable=self.performance_mode_var, 
                                                          onvalue="on", offvalue="off",fg_color=PBLC_Colors.button("disabled"),
                                                          progress_color=PBLC_Colors.button("main"), command=self.performance_switch_event,
                                                          border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.performance_switch.grid(row=0, column=0, padx=10, pady=20)

        if not installed_version > 0 and not installed_beta_version > 0:
            self.performance_switch.configure(state="disabled")

        self.update_manager = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color=PBLC_Colors.frame("main"),bg_color="transparent",corner_radius=15)
        self.update_manager.grid_columnconfigure(0, weight=1)
        self.update_manager.grid(row=3, column=0)

        self.new_builds_img = customtkinter.CTkImage(PBLC_Icons.arrow_up_right(),size=(15,15))
        self.update_self_button = customtkinter.CTkButton(self.update_manager,image=self.new_builds_img, text="Check for new builds",font=('IBM 3270',16),fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.check_for_updates_manager,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.update_self_button.grid(row=0, column=0, padx=20, pady=20)

        if settingsMan.readSettingsValue("program","currently_has_update") == "True":
            self.update_self_button.configure(text="Update Launcher")

            threading.Thread(target=lambda update_button = self.update_self_button,c_start = PBLC_Colors.button("green_confirm"),c_end = PBLC_Colors.button("outline"), dur = 0.2 :widgetAnimation.looping_border_flash(update_button,c_start,c_end,dur),daemon=True).start()

        self.version_data_frame = customtkinter.CTkFrame(self.main_frame,fg_color=PBLC_Colors.frame("main"),bg_color="transparent",corner_radius=15)
        self.version_data_frame.grid(row=4,column=0)
        

        if installed_version > 0:
            display_text = f"PBLC Stable v{installed_version_disp}"
        elif installed_beta_version > 0:
            display_text = f"PBLC Beta v{installed_beta_version_disp} | v{json_data_internal['beta_goal']}"
        else:
            display_text = f"Vanilla Lethal Company"

        self.update_manager_credits = customtkinter.CTkLabel(self.version_data_frame,text=f"Version: {PBLC_Update_Manager_Version}\n\nDeveloped by DarthLilo  |  Testing by ExoticBuilder",font=('IBM 3270',16))
        self.update_manager_credits.grid(row=0, column=0,pady=(10,5),padx=10)
        self.update_manager_version = customtkinter.CTkLabel(self.version_data_frame,text=f"\nCurrently Running: {display_text}",font=('IBM 3270',15))
        self.update_manager_version.grid(row=1, column=0,pady=(5,5))
        self.installed_mod_count = customtkinter.CTkLabel(self.version_data_frame,text=f"({len(os.listdir(modDatabase.folder_path))} Mods)",font=('IBM 3270',15))
        self.installed_mod_count.grid(row=2, column=0,pady=(5,10))

        #Extras 

        logMan.new("Drawing Extras")

        self.main_frame = customtkinter.CTkFrame(self.tabview.tab("Extras"), corner_radius=5, fg_color=PBLC_Colors.frame("main"))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid(row=0, column=0,sticky='nsew')

        


        self.extras_frame_main = customtkinter.CTkFrame(self.main_frame,fg_color=PBLC_Colors.frame("darker"),corner_radius=5)
        self.extras_frame_main.grid_columnconfigure(0, weight=1)
        self.extras_frame_main.grid_columnconfigure(1, weight=1)
        self.extras_frame_main.grid_columnconfigure(2, weight=1)
        self.extras_frame_main.grid_rowconfigure(0, weight=1)
        self.extras_frame_main.grid_rowconfigure(1, weight=1)
        self.extras_frame_main.grid_rowconfigure(2, weight=1)
        self.extras_frame_main.grid(row=0, column=0)

        self.pblc_pack_name = customtkinter.CTkEntry(self.extras_frame_main,placeholder_text="PBLC Version",width=400)
        self.pblc_pack_name.grid(row=0,column=0,padx=(10,5),pady=10)

        self.archive_img = customtkinter.CTkImage(PBLC_Icons.archive(),size=(15,15))
        self.pblc_pack_trigger = customtkinter.CTkButton(self.extras_frame_main,image=self.archive_img,text="",fg_color=PBLC_Colors.button("main"),
                                                         hover_color=PBLC_Colors.button("hover"),border_color=PBLC_Colors.button("outline"),
                                                         border_width=PBLC_Colors.button("outline_size"),width=30,command=lambda:self.export_modpack(True))
        self.pblc_pack_trigger.grid(row=0,column=1,padx=(5,5),pady=10)

        self.file_icon_thing = customtkinter.CTkImage(PBLC_Icons.file(),size=(15,15))
        self.new_version_save = customtkinter.CTkButton(self.extras_frame_main,image=self.file_icon_thing,text="",fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),
                                                        border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"),width=30,command=lambda:self.export_modpack(False))
        self.new_version_save.grid(row=0,column=2,padx=(5,10),pady=10)

        self.pblc_patch_save_list = customtkinter.CTkButton(self.extras_frame_main,width=400,text="Generate Patch Point",command=self.create_patch_point,fg_color=PBLC_Colors.button("main"),
                                                         hover_color=PBLC_Colors.button("hover"),border_color=PBLC_Colors.button("outline"),
                                                         border_width=PBLC_Colors.button("outline_size"))
        self.pblc_patch_save_list.grid(row=1,column=0,padx=(10,5),pady=10)

        self.patch_save_del = customtkinter.CTkImage(PBLC_Icons.trash_can(),size=(15,15))

        self.add_new_file_icon = customtkinter.CTkImage(PBLC_Icons.plus(),size=(15,15))
        self.pblc_patch_save_new = customtkinter.CTkButton(self.extras_frame_main,text="",image=self.add_new_file_icon,width=30,command=self.gen_patch_change,fg_color=PBLC_Colors.button("main"),
                                                         hover_color=PBLC_Colors.button("hover"),border_color=PBLC_Colors.button("outline"),
                                                         border_width=PBLC_Colors.button("outline_size"))
        self.pblc_patch_save_new.grid(row=1,column=2,padx=(5,10),pady=10)

        self.installed_patches = []
        

        self.pblc_special_patch_list = customtkinter.CTkOptionMenu(self.extras_frame_main,width=400,values=self.installed_patches,fg_color=PBLC_Colors.button("main"),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
        self.pblc_special_patch_list.grid(row=2,column=0,padx=(10,5),pady=10)
        if len(self.installed_patches) == 0:
            self.pblc_special_patch_list.set("No extra patches installed!")
        
        self.get_extra_patches()

        self.pblc_special_patch_uninstall = customtkinter.CTkButton(self.extras_frame_main,text="",image=self.patch_save_del,width=30,command=self.uninstall_patches,fg_color=PBLC_Colors.button("main"),
                                                         hover_color=PBLC_Colors.button("hover"),border_color=PBLC_Colors.button("outline"),
                                                         border_width=PBLC_Colors.button("outline_size"))
        self.pblc_special_patch_uninstall.grid(row=2,column=1,padx=(5,5),pady=10)

        self.pblc_special_patch_install = customtkinter.CTkButton(self.extras_frame_main,text="",image=self.add_new_file_icon,width=30,command=self.load_new_patch,fg_color=PBLC_Colors.button("main"),
                                                         hover_color=PBLC_Colors.button("hover"),border_color=PBLC_Colors.button("outline"),
                                                         border_width=PBLC_Colors.button("outline_size"))
        self.pblc_special_patch_install.grid(row=2,column=2,padx=(5,10),pady=10)

        self.main_actions = customtkinter.CTkFrame(self.main_frame,fg_color=PBLC_Colors.frame("darker"),corner_radius=5)
        self.main_actions.grid_columnconfigure(0,weight=1)
        self.main_actions.grid_columnconfigure(1,weight=1)
        self.main_actions.grid_columnconfigure(2,weight=1)
        self.main_actions.grid_rowconfigure(0,weight=1)
        self.main_actions.grid(row=1,column=0)

        self.redownload_mods_img = customtkinter.CTkImage(PBLC_Icons.refresh(),size=(15,15))
        self.redownload_all_mods = customtkinter.CTkButton(self.main_actions,text="Redownload Mods",image=self.redownload_mods_img,command=self.reinstall_all_mods,fg_color=PBLC_Colors.button("main"),
                                                         hover_color=PBLC_Colors.button("hover"),border_color=PBLC_Colors.button("outline"),
                                                         border_width=PBLC_Colors.button("outline_size"))
        self.redownload_all_mods.grid(row=0,column=0,padx=(10,5),pady=10)

        self.uninstall_mods_img = customtkinter.CTkImage(PBLC_Icons.uninstall(),size=(15,15))
        self.uninstall_mods = customtkinter.CTkButton(self.main_actions,text="Uninstall Mods",image=self.uninstall_mods_img,command=self.uninstall_everything,fg_color=PBLC_Colors.button("main"),
                                                         hover_color=PBLC_Colors.button("hover"),border_color=PBLC_Colors.button("outline"),
                                                         border_width=PBLC_Colors.button("outline_size"))
        self.uninstall_mods.grid(row=0,column=1,padx=(5,5),pady=10)

        self.list_installed_mods = customtkinter.CTkButton(self.main_actions,text="Export Mods List",image=self.file_icon_thing,command=self.export_mod_list,fg_color=PBLC_Colors.button("main"),
                                                         hover_color=PBLC_Colors.button("hover"),border_color=PBLC_Colors.button("outline"),
                                                         border_width=PBLC_Colors.button("outline_size"))
        self.list_installed_mods.grid(row=0,column=2,padx=(5,10),pady=10)

        #Mods

        logMan.new("Drawing Mods")

        self.main_frame = customtkinter.CTkFrame(self.tabview.tab("Mods"), corner_radius=0, fg_color="transparent")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid(row=0, column=0,sticky='nsew')

        #self.fetch_mods = customtkinter.CTkButton(self.main_frame, text="Fetch Mods", command=self.fetchModData)
        #self.fetch_mods.grid(row=3, column=0)

        self.thunderstore_mod_frame = thunderstoreModScrollFrame(self.main_frame,fg_color=PBLC_Colors.frame("main"),width=960,height=486,parent=self)
        self.thunderstore_mod_frame.grid(row=0,column=0,sticky="nsew")

        self.url_import_frame = customtkinter.CTkFrame(self.main_frame)
        self.url_import_frame.grid_columnconfigure(0,weight=1)
        self.url_import_frame.grid_columnconfigure(1,weight=1)
        self.url_import_frame.grid_columnconfigure(2,weight=1)
        self.url_import_frame.grid_columnconfigure(3,weight=1)
        self.url_import_frame.grid_rowconfigure(0,weight=1)
        self.url_import_frame.grid(row=1,column=0,sticky='nsew',pady=2)

        self.import_url_box = customtkinter.CTkEntry(self.url_import_frame,width=550,height=10,placeholder_text="Thunderstore Package URL")
        self.import_url_box.grid(row=0,column=0,padx=3,sticky='nsew')
        self.import_url_box.bind("<Return>",lambda mod_frame=self.thunderstore_mod_frame: self.import_thunderstore_url(mod_frame))

        self.import_url_vers_box = customtkinter.CTkEntry(self.url_import_frame,width=130,height=10,placeholder_text="Version (Optional)")
        self.import_url_vers_box.grid(row=0,column=1,padx=3,sticky='nsew')
        self.import_url_vers_box.bind("<Return>",lambda mod_frame=self.thunderstore_mod_frame: self.import_thunderstore_url(mod_frame))

        self.import_from_url = customtkinter.CTkButton(self.url_import_frame,text="Download",fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=lambda mod_frame = self.thunderstore_mod_frame: self.import_thunderstore_url(mod_frame),border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.import_from_url.grid(row=0,column=2,padx=3,sticky='nsew')

        self.check_for_updatesall = customtkinter.CTkButton(self.url_import_frame,text="Scan for Updates",fg_color=PBLC_Colors.button("main"),hover_color=PBLC_Colors.button("hover"),command=self.check_for_updates_all,border_color=PBLC_Colors.button("outline"),border_width=PBLC_Colors.button("outline_size"))
        self.check_for_updatesall.grid(row=0,column=3,padx=3,sticky='nsew')

        self.main_frame = customtkinter.CTkFrame(self.tabview.tab("Config"), corner_radius=0, fg_color="transparent")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid(row=0,column=0,sticky="nsew")
    
        self.config_frame = configSettingScrollFrame(self.main_frame,fg_color="transparent",height=500)
        self.config_frame.grid(row=0,column=0,sticky="nsew")

        logMan.new(f"Welcome to PBLC Update Manager {PBLC_Update_Manager_Version}!")
        if not isScriptFrozen:
            self.main_frame = customtkinter.CTkFrame(self.tabview.tab("Dev"), corner_radius=0, fg_color="transparent")
            self.main_frame.grid_rowconfigure(0, weight=1)
            self.main_frame.grid_columnconfigure(0, weight=1)
            self.main_frame.grid(row=0,column=0,sticky="nsew")
            
            self.devresetbutton = customtkinter.CTkButton(self.main_frame,text="display update ui",command=self.drawUpdateUI)
            self.devresetbutton.grid(row=0,column=0)

            self.teeheebutton = customtkinter.CTkButton(self.main_frame,text="dev func",command=self.tempDevFunc)
            self.teeheebutton.grid(row=1,column=0)
        
        #HIDE LOADING SCREEN
        if loader:
            self.loader_menu.stop_loader()
    
    def drawUpdateUI(self):
        logMan.new("Destroying Main UI")
        self.destroyPBLCUI()
        logMan.new("Drawing Update UI")

        self.update_screen_displayed = True

        self.update_frame = customtkinter.CTkFrame(self,fg_color="black")
        self.update_frame.grid(row=0,column=0,sticky="nsew")
        self.update_frame.grid_columnconfigure(0,weight=1)
        self.update_frame.grid_rowconfigure(0,weight=1)

        self.current_download = customtkinter.CTkFrame(self.update_frame,fg_color=PBLC_Colors.frame("update_ui"),corner_radius=15)
        self.current_download.grid(row=0,column=0,sticky='nsew',padx=40,pady=(20,5))
        self.current_download.grid_rowconfigure(0,weight=1)
        self.current_download.grid_columnconfigure(0,weight=1)

        self.mod_download_frame = modDownloadingScrollFrame(self.current_download,PBLC_Colors.frame("main"),960,880,self)
        self.mod_download_frame.grid(row=0,column=0,sticky='nsew')

        self.current_download_data = customtkinter.CTkFrame(self.update_frame,fg_color=PBLC_Colors.frame("update_ui"),corner_radius=15)
        self.current_download_data.grid(row=1,column=0,sticky='nsew',padx=40,pady=(5,20))
        self.current_download_data.grid_rowconfigure(0,weight=1)
        self.current_download_data.grid_rowconfigure(1,weight=1)
        self.current_download_data.grid_rowconfigure(2,weight=1)
        self.current_download_data.grid_columnconfigure(0,weight=1)
        self.current_download_data.grid_columnconfigure(1,weight=0)
        
        self.pblc_main_status = customtkinter.CTkLabel(self.current_download_data,text="Initializing Download",font=('IBM 3270',20))
        self.pblc_main_status.grid(row=0,column=0,pady=(15,5),padx=10)

        self.bar_container = customtkinter.CTkFrame(self.current_download_data)
        self.bar_container.grid_rowconfigure(0,weight=1)
        self.bar_container.grid_columnconfigure(0,weight=1)
        self.bar_container.grid(row=1,column=0,pady=(5,5))

        self.pblc_progress_total_bar = customtkinter.CTkProgressBar(self.bar_container,width=230,height=15,progress_color=PBLC_Colors.button("main"))
        self.pblc_progress_total_bar.grid(row=0,column=0,pady=(5,5),padx=10)
        self.pblc_progress_total_bar.set(0)

        self.pblc_progress_int = 0
        self.pblc_progress_max = 0
        self.pblc_progress_count = customtkinter.CTkLabel(self.bar_container,text="0/0",font=('IBM 3270',20))
        self.pblc_progress_count.grid(row=0,column=1,pady=(5,5),padx=10)

        self.pblc_elapsed_time = customtkinter.CTkLabel(self.current_download_data,text="00:00:00",font=('IBM 3270',20))
        self.pblc_elapsed_time.grid(row=2,column=0,pady=(5,15),sticky='nsew')

        self.initClock()
    
    def tempEnable(self):
        print('rah')
        #app.mod_download_frame.toggle_thread("inactive_thread_1",True)
    
    def updateProgressBar(self,cur_prog,total,popup=False):
        new_prog = round(cur_prog/total,2)

        if popup:
            if not app.pblc_progress_bar_storage.get() == new_prog:
                app.pblc_progress_bar_popup.update_progress(new_prog)
                app.pblc_progress_bar_popup.update_message(f"{round(new_prog*100)}%")
                app.pblc_progress_bar_storage.set(new_prog)
        else:
            logMan.new("This is a deprecated setting, modify the command used to avoid this!",'error')
            #if not app.pblc_progress_bar.get() == new_prog:
            #    app.pblc_progress_bar.set(new_prog)
            #    app.pblc_progress_value.configure(text=f"{round(new_prog*100)}%")
           
    def updateProgressCount(self,popup=False):
        app.pblc_progress_int += 1
        if popup:
            app.pblc_progress_bar_popup.update_progress(round(app.pblc_progress_int/app.pblc_progress_max,2))
            app.pblc_progress_bar_popup.update_message(f"{app.pblc_progress_int}/{app.pblc_progress_max}")
        else:
            app.pblc_progress_count.configure(text=f"{app.pblc_progress_int}/{app.pblc_progress_max}")
            try:
                app.pblc_progress_total_bar.set(round(app.pblc_progress_int/app.pblc_progress_max,2))
            except ZeroDivisionError:
                app.pblc_progress_total_bar.set(round(0))
    
    def updateProgressMax(self,max,popup=False):
        app.pblc_progress_max = max
        if popup:
            app.pblc_progress_bar_popup.update_message(f"{app.pblc_progress_int}/{app.pblc_progress_max}")
        else:
            app.pblc_progress_count.configure(text=f"{app.pblc_progress_int}/{app.pblc_progress_max}")

    def extendProgressMax(self,amount=1, update=False):
        app.pblc_progress_max += amount
        if update:
            app.pblc_progress_count.configure(text=f"{app.pblc_progress_int}/{app.pblc_progress_max}")
            try:
                app.pblc_progress_total_bar.set(round(app.pblc_progress_int/app.pblc_progress_max,2))
            except ZeroDivisionError:
                app.pblc_progress_total_bar.set(round(0))

    def updateProgressDisplay(self,target,message):
        app.mod_download_frame.threads[target].status(message)
        #app.mod_download_frame.update_status(target,message)

    def updateProgressIcon(self,namespace,name,version):
        target_url = f"https://gcdn.thunderstore.io/live/repository/icons/{namespace}-{name}-{version}.png"
        try:
            geticon = requests.get(target_url)
            fin_img = roundImageCorners(Image.open(BytesIO(geticon.content)),35)
        except Exception:
            fin_img = PBLC_Icons.missing_icon()
            logMan.new("Error while drawing icon, check internet",'warning')
        app.pblc_progress_icon.configure(dark_image=fin_img)

    def updateDownloadStatus(self,newstatus):
        self.pblc_main_status.configure(text=newstatus)

    def destroyPBLCUI(self):
        self.tabview.destroy()
    
    def redrawPBLCUI(self,default_frame="Home"):
        app.kill_clock = True
        app.update_frame.destroy()
        app.drawPBLCUI(default_frame=default_frame,loader=True)
    
    def initClock(self):
        self.start_time = timeMan.now()
        threading.Thread(target=lambda start_time=self.start_time:self.updateClock(start_time),daemon=True).start()
    
    def updateClock(self,start):
        if not app.kill_clock:
            app.pblc_elapsed_time.configure(text=timeMan.time_passed(start,timeMan.now()))
            self.after(1000,func=lambda start=start:self.updateClock(start))
        else:
            app.kill_clock = False
    
    def tempDevFunc(self):
        
        packages = {"KlutzyBubbles-BetterEmotes":{"namespace":"KlutzyBubbles","name":"BetterEmotes","version":"1.5.1"},
                    "RosiePies-Rosies_Moons":{"namespace":"RosiePies","name":"Rosies_Moons","version":"2.0.0"}}

        teehee = downloadQueueMan.queue_packages(packages,True)
        print(teehee)

    def uninstall_everything(self):
        if is_lethal_running():
            return
        logMan.new("Uninstalling all mods!")
        uninstallMods()
        version_man.set_patch("0.0.0")
        extra_patches = os.path.join(getCurrentPathLoc(),"data","extra_patches")
        for patch in os.listdir(extra_patches):
            os.remove(f"{extra_patches}/{patch}")
        app.get_extra_patches()
        self.redrawScrollFrame()
        self.update_manager_version.configure(text=f"\n\nCurrently Running: Vanilla Lethal Company")
        self.update_button_main.configure(text="Install Mods")
        self.installed_mod_count.configure(text="(0 Mods)")
        if settingsMan.readSettingsValue("program","show_beta_options") == "True":
            self.update_button_main_2.configure(text="Install Beta Mods")
        ctkextensions.CTkNotification(master=app, message="Mods uninstalled successfully!", side="right_bottom")

    def gen_patch_change(self):
        if is_lethal_running():
            return
        patch_save = f"{current_file_loc}/data/patch_point.json"
        patch_changes = f"{current_file_loc}/data/patch_changes.json"
        if not os.path.exists(patch_save):
            logMan.new("No patch save found!",'warning')
            ctkextensions.CTkNotification(master=app, message="No patch point file found, please create one first!", side="right_bottom")
            return
        
        logMan.new("Generating changes")
        
        patch_save_data = open_json(patch_save)
        mod_database_local = modDatabase.get()

        new_changes = {
            "new":[]
        }

        for mod in mod_database_local:
            mod_data = modDatabase.get(mod)
            if mod in patch_save_data.keys():
                if mod_data['version'] != patch_save_data[mod]['version']:
                    new_changes['new'].append(f"url_add_mod|{mod_data['author']}|{mod_data['name']}|{mod_data['version']}")
            else:
                new_changes['new'].append(f"url_add_mod|{mod_data['author']}|{mod_data['name']}|{mod_data['version']}")

        for mod in patch_save_data.keys():
            if mod not in mod_database_local:
                new_changes['new'].append(f"delete_mod|{patch_save_data[mod]['author']}|{patch_save_data[mod]['name']}")
        
        with open(patch_changes, "w") as patch_change:
            patch_change.write(json.dumps(new_changes,indent=4))
        
        logMan.new(f"Finished generating changes, find them at {patch_changes}")

    def create_patch_point(self):
        if is_lethal_running():
            return
        prompt_answer = CTkMessagebox(title="PBLC Update Manager",message="Are you sure you would like to create a save point? This may override existing data!",option_2="Yes",option_1="No",button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"),icon=PBLC_Icons.info(True))
        if prompt_answer.get() == "Yes":
            logMan.new("Updating patch save")
            patch_save = f"{current_file_loc}/data/patch_point.json"
            installed_mods = {}
            for mod in modDatabase.get():
                mod_data = modDatabase.get(mod)
                installed_mods[mod] = {}
                installed_mods[mod]['name'] = mod_data['name']
                installed_mods[mod]['author'] = mod_data['author']
                installed_mods[mod]['version'] = mod_data['version']
            with open(patch_save,"w") as patch_point:
                patch_point.write(json.dumps(installed_mods,indent=4))
            ctkextensions.CTkNotification(master=app, message="Created patch save sucsessfully!", side="right_bottom")
    
    def export_modpack(self,zip_file):
        if is_lethal_running():
            return
        
        if zip_file:
            export_folder = os.path.normpath(f"{getCurrentPathLoc()}/exports")
            zip_file_loc = f"{export_folder}/{self.pblc_pack_name.get()}.zip"

            if not os.path.exists(export_folder):
                os.mkdir(export_folder)

            target_files = [doorstop_path,winhttp_path]

            result = compress_zip(zip_file_loc,target_files)
            if result == "CANCELLED":
                CTkMessagebox(title="PBLC Update Manager",message="Error creating modpack zip, make sure you have a working install of BepInEx!",icon=PBLC_Icons.info(True),button_color=PBLC_Colors.button("main"),button_hover_color=PBLC_Colors.button("hover"))
                return
            compress_zip_dir(zip_file_loc,bepinex_path)
            compress_zip_dir(zip_file_loc,modDatabase.folder_path)
        else:
            update_files_path = f"{getCurrentPathLoc()}/update_files"
            json_file_loc = f"{update_files_path}/{self.pblc_pack_name.get()}.json"
            mod_db_local = modDatabase.get()
            if not os.path.exists(update_files_path):
                os.mkdir(update_files_path)

            update_data = {"instructions":[]}

            for mod in mod_db_local:
                mod = modDatabase.get(mod)
                name = mod['name']
                author = mod['author']
                version = mod['version']
                update_data["instructions"].append(f"url_add_mod|{author}|{name}|{version}")

            with open(json_file_loc, "w") as pblc_export_vers:
                pblc_export_vers.write(json.dumps(update_data,indent=4))
    
    def import_thunderstore_url(self,mod_frame):
        if is_lethal_running():
            return
        if not self.pblc_app_is_busy:
            self.pblc_progress_bar_popup = modDownloadPopup(app)
            url_box_input = self.import_url_box.get()
            namespace,name = thunderstore.package_from_url(url_box_input)
            downloadQueueMan.clear_queue()
            package_queue = downloadQueueMan.queue_packages({f"{namespace}-{name}":{"name":name,"author":namespace,"version":"","bar":False,"extend_max":False,"popup":True}},True)
            threading.Thread(target=lambda imp_url = url_box_input, imp_box_url = self.import_url_vers_box.get(), package_queue = package_queue :thunderstore.url_import_entry(imp_url,imp_box_url,package_queue,popup=True),daemon=True).start()
            self.import_url_box.delete(0,len(self.import_url_box.get()))
            self.import_url_vers_box.delete(0,len(self.import_url_vers_box.get()))
    
    def check_for_updates_all(self):
        if is_lethal_running():
            return
        threading.Thread(target=lambda self=self:thunderstore.check_for_updates_all_entry(self),daemon=True).start()
        app.pblc_progress_bar_popup = modDownloadPopup(app,"scan")
    
    def redrawScrollFrame(self):
        logMan.new("Cleaning scroll frame UI")
        for frame in self.thunderstore_mod_frame.winfo_children():
            frame.destroy()

    def check_for_updates_main(self):
        if is_lethal_running():
            return

        checkForUpdates(self,"release")
    
    def check_for_updates_beta(self):
        if is_lethal_running():
            return
        checkForUpdates(self,"beta")
    
    def check_for_updates_manager(self):
        if is_lethal_running():
            return
        checkForUpdatesmanager()

    def performance_switch_thread(self,state):
        time.sleep(0.5)
        commands = {
            "on" : ["url_add_mod|Sligili|HDLethalCompany|1.5.6","download_override|15GWDEYy8aeOmrQbOnNMuPrvvdSzK3mOp|https://www.dropbox.com/scl/fi/ku8cbsptas4xrvx6ny84b/hdlethalcompanyconfig.zip?rlkey=lnfio2kikuz6kqwyymeecpkrp&st=7wi06317&dl=1"],
            "off": ["delete_mod|Sligili|HDLethalCompany|1.5.6"]
        }
        for command in commands[state]:
            decodeDownloadCommand(command,popup=True)
        
        if state == "on":
            thunderstore_ops.call_download_thread("Sligili","HDLethalCompany","1.5.6",False,False,True,True)
        else:
            self.performance_switch.configure(state="normal")
    
    def performance_switch_event(self):
        if is_lethal_running():
            return
        toggle_state = self.performance_mode_var.get()
        self.performance_switch.configure(state="disabled")
        if toggle_state == "on":
            app.pblc_progress_bar_popup = modDownloadPopup(app)
        threading.Thread(target=lambda toggle_state=toggle_state:self.performance_switch_thread(toggle_state),daemon=True).start()

        value_upd = open_json(pblc_vers)
        value_upd["performance_mode"] = toggle_state

        with open(pblc_vers, "w") as patch_change:
            patch_change.write(json.dumps(value_upd))    

    def get_extra_patches(self):
        extra_patches = os.path.join(getCurrentPathLoc(),"data","extra_patches")
        valid_files = []
        for file in os.listdir(extra_patches):
            if file.endswith(".json"):
                valid_files.append(file)
        self.installed_patches = valid_files
        try:
            self.pblc_special_patch_list.set(self.installed_patches[0])
        except IndexError:
            self.pblc_special_patch_list.set("No extra patches installed!")

        self.pblc_special_patch_list.configure(values=self.installed_patches)
    
    def load_new_patch(self):
        if is_lethal_running():
            return
        extra_patches = os.path.join(getCurrentPathLoc(),"data","extra_patches")
        filetypes = [('PBLC JSON Files', '*.json'), ('All files', '*.*')]
        target_file = customtkinter.filedialog.askopenfilename(filetypes=filetypes)

        if not os.path.exists(target_file):
            logMan.new("No patch file selected!",'warning')
            return

        patch_data = open_json(target_file)
        
        try:
            patch_data["instructions"]
        except KeyError:
            logMan.new("Invalid patch file!",'warning')
            return
        new_location = f"{extra_patches}/{os.path.basename(target_file)}"
        shutil.copy(target_file,new_location)

        app.pblc_progress_bar_popup = modDownloadPopup(app)

        threading.Thread(target=lambda patches = patch_data["instructions"],target_file=new_location:self.install_patches(patches,target_file),daemon=True).start()
    
    def install_patches(self,patches,target_file):
        time.sleep(0.2)

        self.fpi_patches = patches
        self.fpi_target_file = target_file

        queueMan.clearQueue()
        
        custom_patches_queue = {}

        for patch in patches:
            decodeDownloadCommand(patch,popup=True,record_deps=True)
            if str(patch).startswith("url_add_mod"):
                split_patch = str(patch).split("|")
                custom_patches_queue[f"{split_patch[1]}-{split_patch[2]}"] = {"name":split_patch[2],"author":split_patch[1],"version":split_patch[3],"bar":False,"extend_max":False,"popup":True}
        downloadQueueMan.clear_queue()
        package_queue = downloadQueueMan.queue_packages(custom_patches_queue,True)
        self.fpi_full_patches = package_queue
        queueMan.queuePackages(package_queue)
        queueMan.execute(False,1,True)
        
    def finish_patch_install(self):
        target_file = self.fpi_target_file
        all_patches = self.fpi_full_patches

        internal_patch_file = open_json(target_file)
        if "removal_instructions" not in internal_patch_file:
            internal_patch_file["removal_instructions"] = []
        for patch in all_patches:
            internal_patch_file["removal_instructions"].append(f"delete_mod|{all_patches[patch]['namespace']}|{all_patches[patch]['name']}")
        
        with open(target_file, "w") as patch_change:
            patch_change.write(json.dumps(internal_patch_file,indent=4))
        
        app.pblc_progress_bar_popup.close()
        app.new_mods_list = []
        self.get_extra_patches()
    
    def uninstall_patches(self):
        if is_lethal_running():
            return
        extra_patches = os.path.join(getCurrentPathLoc(),"data","extra_patches")
        target_file = os.path.join(extra_patches,self.pblc_special_patch_list.get())
        if not os.path.exists(target_file):
            return
        
        try:
            removal_patches = open_json(target_file)["removal_instructions"]
        except Exception as e:
            logMan.new(f"Error when trying to remove {target_file}, this is most likely due to a corrupted patch file or invalid json formatting",'error')
            logMan.new(traceback.format_exc(),'error')
            ctkextensions.CTkNotification(master=app, message="Error when removing patch!", side="right_bottom")
            return

        for patch in removal_patches:
            try:
                decodeDownloadCommand(patch)
            except KeyError:
                pass
        
        os.remove(target_file)
        self.get_extra_patches()

    def reinstall_all_mods(self):
        if is_lethal_running():
            return
        mod_list = modDatabase.get(detailed=True)
        
        if len(mod_list) == 0:
            user_response = CTkMessagebox(title="PBLC Update Manager",message="You have no mods to reinstall!",button_color=PBLC_Colors.button("main"),icon=PBLC_Icons.info(True),button_hover_color=PBLC_Colors.button("hover"))
            return

        user_response = CTkMessagebox(title="PBLC Update Manager",message=f"Are you sure you would like to redownload {len(mod_list)} mods? This make take a while!",option_1="No",option_2="Yes",
                                      button_color=PBLC_Colors.button("main"),icon=PBLC_Icons.info(True),button_hover_color=PBLC_Colors.button("hover"))

        if user_response.get() == "Yes":

            self.drawUpdateUI()
            self.updateProgressMax(len(mod_list))
            threading.Thread(target=lambda mod_db = mod_list:thunderstore.batch_url_import(mod_db,bar=True),daemon=True).start()
    
    def export_mod_list(self):
        if is_lethal_running():
            return
        mod_db_local = modDatabase.get()
        installed_mods_txt = os.path.join(getCurrentPathLoc(),"data","installed_mods.txt")
        installed_mod_data = []
        for mod in mod_db_local:
            mod = modDatabase.get(mod)

            name = mod['name']
            version = mod['version']
            installed_mod_data.append(f"{name} ({version})")

        formatted_data = '\n'.join(installed_mod_data)
        
        with open(installed_mods_txt, "w") as mods_list_stuff:
            mods_list_stuff.write(formatted_data)
        finished = CTkMessagebox(title="PBLC Update Manager",message="Exported mods list to \'data/installed_mods.txt\'!",
                                 button_color=PBLC_Colors.button("main"),icon=PBLC_Icons.info(True),button_hover_color=PBLC_Colors.button("hover"))

def on_pblc_close():
    logMan.close()
    app.destroy()

app = PBLCApp()
hPyT.maximize_minimize_button.hide(app)
app.protocol("WM_DELETE_WINDOW",on_pblc_close)
try:
    app.mainloop()
except Exception as e:
    logMan.new(traceback.format_exc(),'error')