import validators, os, requests, traceback, json, webbrowser, gdown, shutil, subprocess, sys
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from urllib import request
from urllib.error import HTTPError
from packaging import version
from .Logging import Logging
from .Maths import Maths
from .Assets import Assets
from .Filetree import Filetree
from .Game import Game
from PIL import Image
from io import BytesIO

class Networking: 

    github_repo_latest_release = "https://api.github.com/repos/DarthLilo/PBLC-Update-Manager/releases/latest"
    PBLCVersion = ""
    CurFolder = ""

    def UrlValidator(url):
        if validators.url(url) != True:
            Logging.New(f"[{url}] is not a valid URL!",'warning')
            return False
        
        # REMOVING HTTP KEYWORDS
        url = url.replace("https://","")
        url = url.replace("http://","")

        # Splits URL into a list
        url_segments = str(url).split("/")
        verify_link_requirements = ["thunderstore.io","c",Game.ts_url_prefix,"p"]

        # Verifies that the minimum requirements are present in the split link
        if set(verify_link_requirements) <= set(url_segments):
            Logging.New(f"[{url}] is a valid {Game.game_id} Thunderstore package link!")
            return url_segments

        return False
    
    def RequestWebData(url):
        headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0)"
        }
        req = request.Request(url,headers=headers)
        return req
    
    def CompareVersions(host_version,client_version):
        """Compares two versions to see if the host version is higher than the client version"""
        return version.Version(host_version) > version.Version(client_version)

    def DownloadFromUrl(url,location,print_length=None,feedback_func=None):
        Logging.New(f"Downloading [{url}]...")

        try:
            package_request = requests.get(url,stream=True)
        except Exception as e:
            Logging.New(f"Error when downloading {url}, please verify your internet connection and try again!")
            return
        download_percentage = 0

        total_size_in_bytes = int(package_request.headers.get('content-length',0))

        with open(location,'wb') as download_package:
            chunk_count = 0
            for chunk in package_request.iter_content(chunk_size=1024):
                download_package.write(chunk)
                chunk_count += len(chunk)

                download_percentage_local = Maths.DownloadPercent(chunk_count,total_size_in_bytes,True)
                if callable(feedback_func) and download_percentage_local != download_percentage: 
                    feedback_func(download_percentage_local)
                    download_percentage = download_percentage_local
                
                if callable(print_length):
                    print_length(f"{Maths.ConvertSize(chunk_count)}")
    
    def OpenURL(url):
        Logging.New(f"Opening {url}")
        webbrowser.open_new(url)
    
    def DownloadFromGoogleDrive(source,destination):
        if not source or not destination:
            Logging.New("Please provide a valid source/destination!",'error')
            return "invalid"
        Logging.New(f"Beginning download of {source} from Google Drive")
        try:
            gdown.download(id=source,output=destination,quiet=True)
            return "finished"
        except gdown.exceptions.FileURLRetrievalError:
            Logging.New(f"{source} has too many requests!")
            return "too_many_requests"
    
    def GetURLImage(url):
        """Returns a PIL Image from a URL"""
        try:
            fin_image = Image.open(BytesIO(requests.get(url).content))
        except Exception as e:
            Logging.New(traceback.format_exc(),'error')
            fin_image = Image.open(Assets.getResource(Assets.IconTypes.missing))

        return fin_image
    
    def DownloadURLImage(url, destination):
        """Saves an image from a URL"""
        opener = request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        request.install_opener(opener)
        request.urlretrieve(url, destination)

    def IsURL(url):
        if validators.url(url) != True:
            return False
        return True
    
    def CheckForUpdatesManager():
        Logging.New("Checking for PBLC Updates")
        try:
            github_api_response = json.loads(request.urlopen(Networking.github_repo_latest_release).read().decode())
        except Exception as e:
            Logging.New("Error when checking for updates, please verify your connection to the internet!")
            return
        latest_manager =  str(github_api_response['tag_name'])

        if Networking.CompareVersions(latest_manager,Networking.PBLCVersion):
            Logging.New("Updates available!")
            dlg = ConfirmUpdate("There are updates available, would you like to update?")
            result = dlg.exec()
            if result:
                Networking.DownloadLauncherUpdate(github_api_response)
        else:
            Logging.New("No updates found.")
    
    def DownloadLauncherUpdate(github_api_response):
        Logging.New("Updating launcher")
        zip_link = github_api_response['assets'][0]['browser_download_url']
        temp_download_folder = os.path.normpath(f"{Networking.CurFolder}/download_cache")
        target_zip  = f"{temp_download_folder}/latest_manager.zip"

        if os.path.exists(temp_download_folder):
            shutil.rmtree(temp_download_folder)
        os.mkdir(temp_download_folder)

        request.urlretrieve(zip_link,target_zip)

        Logging.New("Download finished")
        Filetree.DecompressZip(target_zip,temp_download_folder)

        py_result = subprocess.run(['py','--version'],capture_output=True,text=True)
        python_result = subprocess.run(['python','--version'],capture_output=True,text=True)

        if python_result.returncode == 0:
                subprocess.Popen(["python",f"{Networking.CurFolder}/Updater.py"])
                return True
        elif py_result.returncode == 0:
            subprocess.Popen(["py",f"{Networking.CurFolder}/Updater.py"])
            return True
        
        else:
            pass
        sys.exit()

        return

class ConfirmUpdate(QDialog):
    def __init__(self,message):
        super().__init__()

        self.setWindowTitle("Launcher Update")
        self.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))

        Buttons = (
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        self.button_box = QDialogButtonBox(Buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        self.message = QLabel(message)
        layout.addWidget(self.message)
        layout.addWidget(self.button_box)