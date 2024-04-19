import json
import os
import winreg
import vdf
import shutil
import zipfile
import ctypes
import gdown
import sys
import customtkinter
import pyglet
from PIL import Image
from urllib import request
pyglet.font.add_file('Minecraft_Five.otf')
pyglet.font.add_file('Minecraft_Five_Bold.otf')

PBLC_Update_Manager_Version = "0.0.0"

github_repo_versoin_db = "https://raw.githubusercontent.com/DarthLilo/PBLC-Update-Manager/master/version_db.json"
github_repo_latest_release = "https://api.github.com/repos/DarthLilo/PBLC-Update-Manager/releases/latest"

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

def custom_message_box(message, title, style):
    return ctypes.windll.user32.MessageBoxW(0, message, title, style)

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def newEmptyRow(self,row_number,spacing):
        self.empty_row = customtkinter.CTkLabel(self.main_frame, text="")
        self.empty_row.grid(row=row_number, column=0, padx=20, pady=spacing)

steam_install_path = str(read_reg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\\Wow6432Node\\Valve\\Steam", k = 'InstallPath'))
steamapps = steam_install_path+"\steamapps"
library_folders = steamapps+"\libraryfolders.vdf"
libdata = vdf.load(open(library_folders))
lethal_company_steamid = "1966720"

def locate_lethal_company():
    for library in libdata['libraryfolders']:
        cur_lib = libdata['libraryfolders'][library]
        apps = cur_lib["apps"]
        if lethal_company_steamid in apps:
            lethal_path = os.path.normpath(f"{cur_lib['path']}/steamapps/common/Lethal Company")
            return lethal_path

def download_from_google_drive(source,destination):
    print(f"Beginning download of {source} from Google Drive...")
    gdown.download(id=source,output=destination)


LC_Path = locate_lethal_company()
downloads_folder = os.path.normpath(f"{LC_Path}/downloads")
pblc_vers = os.path.normpath(f"{LC_Path}/pblc_version")
bepinex_path = os.path.normpath(f"{LC_Path}/BepInEx")
doorstop_path = os.path.normpath(f"{LC_Path}/doorstop_config.ini")
winhttp_path = os.path.normpath(f"{LC_Path}/winhttp.dll")

#checking for updates

if os.path.exists(pblc_vers):
    installed_version = str(open_json(pblc_vers)['version']).replace(".","")
    installed_beta_version = str(open_json(pblc_vers)['beta_version']).replace(".","")
else:
    installed_version = "0"
    installed_beta_version = "0"



def download_update(update_data):
    latest_update_zip = f"{downloads_folder}/{update_data['name']}.zip"
    download_from_google_drive(update_data['source'],latest_update_zip)
    return latest_update_zip

def decompress_zip(latest_update_zip,destination):
    print("Unzipping file...")
    with zipfile.ZipFile(latest_update_zip, 'r') as zip_ref:
        zip_ref.extractall(destination)
    os.remove(latest_update_zip)

def startUpdate(update_data,update_type):
    try:
        print("Update Available, beginning download...")

        if not os.path.exists(downloads_folder):
            os.mkdir(downloads_folder)

        latest_update_zip = download_update(update_data)

        clear_files = [bepinex_path,doorstop_path,winhttp_path]
        for i in range(0,3):
            f = clear_files[i]
            if os.path.exists(f):
                if os.path.isdir(f):
                    shutil.rmtree(f)
                elif os.path.isfile(f):
                    os.remove(f)
        
        decompress_zip(latest_update_zip,LC_Path)
        shutil.rmtree(downloads_folder)
        print("Updating version cache...")

        current_installed_versions = open_json(pblc_vers)

        if update_type == "release":
            current_installed_versions["version"] = update_data['version']
            current_installed_versions["beta_version"] = "0.0.0"
        else:
            current_installed_versions["beta_version"] = update_data['beta_version']
            current_installed_versions["version"] = "0.0.0"
            
        with open(pblc_vers, "w") as pblc_vers_upd:
            pblc_vers_upd.write(json.dumps(current_installed_versions))

        ctypes.windll.user32.MessageBoxW(0, "Succsessfully installed update!", "PBLC Update Manager")
    except:
        ctypes.windll.user32.MessageBoxW(0, "Error (ask lilo this message isn't supposed to show up LMFAO)", "PBLC Update Manager")

def updateLauncher(github_api_launcher):
    print("Beginning launcher update download...")

    zip_link = github_api_launcher['zipball_url']

    temp_download_folder = os.path.normpath(f"{os.path.dirname(__file__)}/download_cache")
    target_zip = f"{temp_download_folder}/latest_launcher.zip"

    if os.path.exists(temp_download_folder):
        shutil.rmtree(temp_download_folder)
        os.mkdir(temp_download_folder)
    else:
        os.mkdir(temp_download_folder)

    request.urlretrieve(zip_link,target_zip)

    print("Download finished, beginning extraction...")

    decompress_zip(target_zip,temp_download_folder)

def checkForUpdates(update_type):

    print("Checking for updates...")

    #fetching latest version
    #github_repo_json = json.loads(request.urlopen(github_repo_versoin_db).read().decode())
    github_repo_json = open_json("version_db.json")
    latest_version = str(github_repo_json[update_type]['version']).replace(".","") if update_type == "release" else str(github_repo_json[update_type]['beta_version']).replace(".","")


    #RELEASE
    if update_type == "release":

        if installed_version < latest_version:
            print("New Update Found.")
            prompt_answer = ctypes.windll.user32.MessageBoxW(0,f"An update is available, would you like to install it?\n\n\n{github_repo_json[update_type]['description']}\nReleased: {github_repo_json[update_type]['release_date']}\nVersion: {github_repo_json[update_type]['version']}","PBLC Update Manager",4)
            if prompt_answer == 6:
                startUpdate(github_repo_json[update_type],update_type)
        elif not os.path.exists(bepinex_path) or not os.path.exists(doorstop_path) or not os.path.exists(winhttp_path):
            print("Vanilla or broken version found.")
            prompt_answer = ctypes.windll.user32.MessageBoxW(0,f"Vanilla or broken version detected, would you like to install the latest mods?\n\n\n{github_repo_json[update_type]['description']}\nReleased: {github_repo_json[update_type]['release_date']}\nVersion: {github_repo_json[update_type]['version']}","PBLC Update Manager",4)
            if prompt_answer == 6:
                startUpdate(github_repo_json[update_type],update_type)
        else:
            print("No updates found.")
            ctypes.windll.user32.MessageBoxW(0, "No updates available.", "PBLC Update Manager")
    

    #BETA
    else:
        if installed_beta_version < latest_version:
            print("New Beta Found.")
            prompt_answer = ctypes.windll.user32.MessageBoxW(0,f"A new beta is available, would you like to install it?\n\n\n{github_repo_json[update_type]['description']}\nReleased: {github_repo_json[update_type]['release_date']}\nBeta Version: {github_repo_json[update_type]['beta_version']}\nVersion: {github_repo_json[update_type]['version']}","PBLC Update Manager",4)
            if prompt_answer == 6:
                startUpdate(github_repo_json[update_type],update_type)
        elif not os.path.exists(bepinex_path) or not os.path.exists(doorstop_path) or not os.path.exists(winhttp_path):
            print("Vanilla or broken version found.")
            prompt_answer = ctypes.windll.user32.MessageBoxW(0,f"Vanilla or broken version detected, would you like to install the latest beta mods?\n\n\n{github_repo_json[update_type]['description']}\nReleased: {github_repo_json[update_type]['release_date']}\nBeta Version: {github_repo_json[update_type]['beta_version']}\nVersion: {github_repo_json[update_type]['version']}","PBLC Update Manager",4)
            if prompt_answer == 6:
                startUpdate(github_repo_json[update_type],update_type)
        else:
            print("No updates found.")
            ctypes.windll.user32.MessageBoxW(0, "No updates available.", "PBLC Update Manager")

def checkForUpdatesLauncher():
    github_api_launcher = json.loads(request.urlopen(github_repo_latest_release).read().decode())
    latest_launcher = str(github_api_launcher['tag_name']).replace(".","")
    current_launcher = PBLC_Update_Manager_Version.replace(".","")

    if current_launcher < latest_launcher:
        print("New Launcher Update!")
        updateLauncher(github_api_launcher)

#UI MANAGEMENT
class PBLCApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        self.title("Lethal Company Update Manager")
        self.resizable(False,False)
        self.iconbitmap(resource_path("pill_bottle.ico"))

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        #images
        self.ice_cube_logo = customtkinter.CTkImage(Image.open(resource_path("pill_bottle.jpg")),size=(1050, 100))

        #frame
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.main_frame_logo = customtkinter.CTkLabel(self.main_frame, text="", image=self.ice_cube_logo)
        self.main_frame_logo.grid(row=0, column=0, padx=20, pady=20)

        self.lethal_install_border = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color="#191919")
        self.lethal_install_border.grid_columnconfigure(0, weight=1)
        self.lethal_install_border.grid(row=1, column=0)

        self.lci_label = customtkinter.CTkLabel(self.lethal_install_border,text="Lethal Company Install Location:",font=('Minecraft Five',15))
        self.lci_label.grid(row=0, column=0,padx=15,pady=10)
        
        self.lethal_install_path = customtkinter.CTkLabel(self.lethal_install_border,text=LC_Path)
        self.lethal_install_path.grid(row=1, column=0,padx=15,pady=10)

        self.actions_border = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color="#191919")
        self.actions_border.grid_columnconfigure(0, weight=1)
        self.actions_border.grid(row=2, column=0)

        self.update_button_main = customtkinter.CTkButton(self.actions_border, text="Check For Updates",command=self.check_for_updates_main)
        self.update_button_main.grid(row=0, column=0, padx=20, pady=20)

        self.update_button_main_2 = customtkinter.CTkButton(self.actions_border, text="Check For Updates (BETA)",command=self.check_for_updates_beta)
        self.update_button_main_2.grid(row=0, column=1, padx=20, pady=20)

        newEmptyRow(self,2,30)
        newEmptyRow(self,3,20)

        self.update_launcher = customtkinter.CTkFrame(self.main_frame,width=100,height=100,fg_color="#191919")
        self.update_launcher.grid_columnconfigure(0, weight=1)
        self.update_launcher.grid(row=4, column=0)

        self.update_self_button = customtkinter.CTkButton(self.update_launcher, text="Check for Launcher Updates",command=self.check_for_updates_launcher)
        self.update_self_button.grid(row=0, column=0, padx=20, pady=20)


    # click_methods
    def check_for_updates_main(self):
        checkForUpdates("release")
    
    def check_for_updates_beta(self):
        checkForUpdates("beta")
    
    def check_for_updates_launcher(self):
        checkForUpdatesLauncher()

app = PBLCApp()
app.mainloop()