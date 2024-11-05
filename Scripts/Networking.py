import validators, os, requests, traceback, json, webbrowser, gdown
from PyQt6.QtGui import QIcon, QPixmap
from urllib import request
from urllib.error import HTTPError
from packaging import version
from .Logging import Logging
from .Maths import Maths
from .Assets import Assets
from PIL import Image
from io import BytesIO

class Networking: 

    def UrlValidator(url):
        if validators.url(url) != True:
            Logging.New(f"[{url}] is not a valid URL!",'warning')
            return False
        
        # REMOVING HTTP KEYWORDS
        url = url.replace("https://","")
        url = url.replace("http://","")

        # Splits URL into a list
        url_segments = str(url).split("/")
        verify_link_requirements = ["thunderstore.io","c","lethal-company","p"]

        # Verifies that the minimum requirements are present in the split link
        if set(verify_link_requirements) <= set(url_segments):
            Logging.New(f"[{url}] is a valid Lethal Company Thunderstore package link!")
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

        package_request = requests.get(url,stream=True)
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
            gdown.download(id=source,output=destination)
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