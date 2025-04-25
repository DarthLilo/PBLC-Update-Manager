from PyQt6.QtCore import QObject, pyqtSignal

import queue, json, threading, time, os, random, traceback, concurrent.futures
from .Logging import Logging
from .Util import Util
from .Cache import Cache
from .Config import Config
from .Thunderstore import Thunderstore
from .Networking import Networking
from .Game import Game
from packaging import version

class QueueMan():

    max_threads = 6 #int(Config.Read("performance","max_download_threads","value"))
    package_length = 0
    package_progression = 0

    package_queue = queue.Queue()

    def __init__(self):
        QueueMan.max_threads = int(Config.Read("performance","max_download_threads","value"))

    def Debug():

        QueueMan.ClearQueue()
        QueueMan.QueuePackage("DarthLilo","BabyManeater","1.1.2")
        QueueMan.QueuePackage("DarthLilo","LilosScrapExtension","1.4.0")
        threading.Thread(target=QueueMan.Start(),daemon=True)

        return
    
    def QueuePackage(author,name,version):
        package = {
            "author":author,
            "name":name,
            "version":version
        }
        QueueMan.package_queue.put(package)

        try:
            package_dependencies = Cache.Get(author,name,version)['dependencies']
        except KeyError:
            Logging.New(f"Error getting dependencies for {author}-{name}")
            return
        if package_dependencies:
            for dependency in package_dependencies:
                split_dependency = dependency.split("-")
                if str(dependency).__contains__("BepInEx-BepInExPack-") or f"{split_dependency[0]}-{split_dependency[1]}" in Cache.LoadedMods:
                    continue
                QueueMan.QueuePackage(split_dependency[0],split_dependency[1],split_dependency[2])
    
    def QueuePackages(packages):
        for package in packages:
            QueueMan.QueuePackage(package['author'],package['name'],package['version'])
    
    def QueueCleanup(downloads):
        queued_files = {}

        #for download in downloads:
        while not downloads.empty():
            download = downloads.get()

            package_name = f"{download['author']}-{download['name']}"
            new_version  = version.parse(download['version'])

            if package_name in queued_files:
                existing_version = version.parse(queued_files[package_name]['version'])

                if new_version > existing_version:
                    Logging.New(f"Updating {package_name} from version ({existing_version}) to ({new_version})")
                    queued_files[package_name] = download
                else:
                    Logging.New(f"Skipping {package_name}, a newer or same version has already been queued")
            else:
                Logging.New(f"Queueing {package_name} ({new_version})...")
                queued_files[package_name] = download
        
        queue_data = [download_data for download_data in queued_files.values()]

        QueueMan.package_length = len(queue_data)

        return queue_data
    
    def Start(overrides_function=None,update=False, emit_method=None,thread_display_method=None,close_download_method=None,loading_screen_method=None,set_global_percent_method=None,finish_func=None):
        """Starts the multithreaded download based on current queue, must be setup prior to launching download!
        This should also be run inside of its own thread to prevent program freezes!"""

        Logging.New("Starting multithreaded download")
        QueueMan.package_progression = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=QueueMan.max_threads) as executor:
            clean_queue = QueueMan.QueueCleanup(QueueMan.package_queue)
            
            Config.Write("general","major_task_running",True)

            multithread_download_queue = {}

            for index, download_data in enumerate(clean_queue):
                thread = executor.submit(QueueMan.DownloadFile, download_data, index % QueueMan.max_threads, emit_method, thread_display_method, set_global_percent_method)
                multithread_download_queue[thread] = download_data

            for thread in concurrent.futures.as_completed(multithread_download_queue):
                download_data = multithread_download_queue[thread]
                try:
                    thread.result()
                except Exception as e:
                    Logging.New(f"Download of {download_data} failed with exception {e}", 'error')
                else:
                    Logging.New(f"{download_data} finished!")
            
            Config.Write("general","major_task_running",False)
            Logging.New("All download processes finished!")

            if callable(overrides_function):
                overrides_function(update,close_download_method,loading_screen_method,finish_func) # execute override function
            elif callable(finish_func):
                finish_func()


    def ClearQueue():
        QueueMan.package_length = 0
        QueueMan.package_progression = 0
        QueueMan.package_queue = queue.Queue()
            
    class DownloadFile:

        def __init__(self, download_data, worker_index, emit_method, thread_display_method, set_global_percent_method):
            self.download_data = download_data
            self.worker_index = worker_index
            self.emit_method = emit_method
            self.thread_display_method = thread_display_method
            self.set_global_percent_method = set_global_percent_method
            self.package_prefix = f"{download_data['author']}-{download_data['name']}"
            self.download()
        
        def download(self):
            if not os.path.exists(Cache.SelectedModpack):
                Logging.New("Please select a modpack first!")
                return
            
            if self.package_prefix in Cache.LoadedMods:
                Logging.New(f"{self.package_prefix} is already installed, skipping!")
                return

            mod_location, author, name, mod_version, mod_files = Thunderstore.Download(author=self.download_data['author'],mod=self.download_data['name'],mod_version=self.download_data['version'],
                                                                                   feedback_func=self.update_percentage,thread_display=self.UpdateThreadDisplay)
            self.AddPackageFiles(author,name,mod_version,mod_files)
            self.LoadMod(mod_location)

            QueueMan.package_progression += 1
            if callable(self.set_global_percent_method): self.set_global_percent_method((QueueMan.package_progression/QueueMan.package_length)*100)
            
            Logging.New(f"Finished installing ({author}-{name}-{mod_version})")
        
        def UpdateThreadDisplay(self):
            if callable(self.thread_display_method): self.thread_display_method(self.worker_index,self.download_data['author'],self.download_data['name'],self.download_data['version'])

        def AddPackageFiles(self,author,name,mod_version,files):
            target_mod_json = f"{Cache.SelectedModpack}/BepInEx/plugins/{author}-{name}-{mod_version}/mod.json"
            mod_json = {}
            mod_json['author'] = author
            mod_json['name'] = name
            mod_json['mod_version'] = mod_version
            mod_json['enabled'] = True
            mod_json['files'] = files
            mod_json['has_updates'] = False
            mod_json['url'] = f"https://thunderstore.io/c/{Game.ts_url_prefix}/p/{author}/{name}/"

            Util.WriteJson(target_mod_json,mod_json)
        
        def LoadMod(self,path):
            full_mod_name = os.path.basename(path).split("-")
            author = full_mod_name[0]
            name = full_mod_name[1]

            new_mod = {
                "json_file": f"{path}/mod.json",
                "icon": f"{path}/icon.png",
                }

            Cache.LoadedMods[f"{author}-{name}"] = new_mod
            
        
        def update_percentage(self,value):
            if callable(self.emit_method): self.emit_method(self.worker_index,value)