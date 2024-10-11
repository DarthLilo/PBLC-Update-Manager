import validators, os, requests, traceback, json, webbrowser
from urllib import request
from urllib.error import HTTPError
from packaging import version
from .Logging import Logging
from .Maths import Maths

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

    def DownloadFromUrl(url,location,print_length=False):
        Logging.New(f"Downloading [{url}]...")

        package_request = requests.get(url,stream=True)

        total_size_in_bytes = int(package_request.headers.get('content-length',0))

        with open(location,'wb') as download_package:
            chunk_count = 0
            for chunk in package_request.iter_content(chunk_size=1024):
                download_package.write(chunk)
                chunk_count += len(chunk)
                #download_percentage = Maths.DownloadPercent(chunk_count,total_size_in_bytes,True)
                if print_length: Logging.New(f"Downloading... [{Maths.ConvertSize(chunk_count)}]")
    
    def OpenURL(url):
        Logging.New(f"Opening {url}")
        webbrowser.open_new(url)
                    