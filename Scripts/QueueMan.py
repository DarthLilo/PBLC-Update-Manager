import queue, threading, os, concurrent.futures, traceback
from .Logging import Logging
from .Util import Util
from .Cache import Cache
from .Config import Config
from .Thunderstore import Thunderstore
from .Game import Game
from .Networking import Networking
from packaging import version

class QueueMan():

    max_threads = 6 #int(Config.Read("performance","max_download_threads","value"))
    package_length = 0
    package_progression = 0

    package_queue = queue.Queue()
    cache_queue = queue.Queue()

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
        QueueMan.cache_queue.put(package)

        try:
            package_dependencies = Cache.Get(author,name,version)['dependencies']
        except KeyError:
            Logging.New(f"Error getting dependencies for {author}-{name}, this is typically due to an outdated cache file!",'error')
            Logging.New(f"Exception during depedency check:\n {traceback.format_exc()}",'warning')
            Logging.New(f"Cache file for [{author}-{name}-{version}]: \n{Cache.Get(author,name,version)}", 'debug')
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
    
    def Start(overrides_function=None,update=False, worker=None, finish_func=None):
        """Starts the multithreaded download based on current queue, must be setup prior to launching download!
        This should also be run inside of its own thread to prevent program freezes!"""

        # Caching Thumbnails
        QueueMan.cache_package_progression = 0
        worker.status_update.emit("Preparing for Download")
        with concurrent.futures.ThreadPoolExecutor(max_workers=QueueMan.max_threads) as executor:
            clean_queue = QueueMan.QueueCleanup(QueueMan.cache_queue)

            multithread_download_queue = {}

            for index, download_data in enumerate(clean_queue):
                thread = executor.submit(QueueMan.DownloadFile,
                                         download_data,
                                         index % QueueMan.max_threads,
                                         worker,
                                         True)
                multithread_download_queue[thread] = download_data
            
            for thread in concurrent.futures.as_completed(multithread_download_queue):
                download_data = multithread_download_queue[thread]
                try:
                    thread.result()
                except Exception as e:
                    Logging.New(f"Download of {download_data} failed!", 'error')
                else:
                    Logging.New(f"{download_data} finished!")


        Logging.New("Starting multithreaded download")
        QueueMan.package_progression = 0
        worker.status_update.emit("Downloading Mods")
        with concurrent.futures.ThreadPoolExecutor(max_workers=QueueMan.max_threads) as executor:
            clean_queue = QueueMan.QueueCleanup(QueueMan.package_queue)
            
            Config.Write("general","major_task_running",True)

            multithread_download_queue = {}

            for index, download_data in enumerate(clean_queue):
                thread = executor.submit(QueueMan.DownloadFile, 
                                         download_data, 
                                         index % QueueMan.max_threads, 
                                         worker)
                multithread_download_queue[thread] = download_data

            for thread in concurrent.futures.as_completed(multithread_download_queue):
                download_data = multithread_download_queue[thread]
                try:
                    thread.result()
                except Exception as e:
                    Logging.New(f"Download of {download_data} failed!", 'error')
                else:
                    Logging.New(f"{download_data} finished!")
            
            Config.Write("general","major_task_running",False)
            Logging.New("All download processes finished!")
            
            if callable(overrides_function):
                overrides_function(update,worker.close_download_screen,worker.loading_screen_trigger,finish_func) # execute override function
            else:
               worker.finish_func.emit()

    def ClearQueue():
        QueueMan.package_length = 0
        QueueMan.package_progression = 0
        QueueMan.package_queue = queue.Queue()

    class DownloadFile:

        def __init__(self, download_data, worker_index, worker, cache_only=False):
            self.download_data = download_data
            self.worker_index = worker_index
            self.worker = worker
            self.package_prefix = f"{download_data['author']}-{download_data['name']}"
            if cache_only:
                self.cache_thumbnail()
            else:
                self.download()
        
        def cache_thumbnail(self):
            img_path = os.path.join(Cache.ModIconCache,f"{self.download_data['author']}-{self.download_data['name']}-{self.download_data['version']}.png")
            if os.path.exists(img_path):
                return
            image = Networking.GetURLImage(f"https://gcdn.thunderstore.io/live/repository/icons/{self.download_data['author']}-{self.download_data['name']}-{self.download_data['version']}.png")
            image.save(os.path.join(Cache.ModIconCache,f"{self.download_data['author']}-{self.download_data['name']}-{self.download_data['version']}.png"))
            QueueMan.cache_package_progression += 1

            if self.worker:
                self.worker.set_global_percent.emit(
                    (QueueMan.cache_package_progression/QueueMan.package_length)*100
                )


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
            
            if self.worker:
                self.worker.set_global_percent.emit(
                    (QueueMan.package_progression/QueueMan.package_length)*100
                )
            #if callable(self.set_global_percent_method): self.set_global_percent_method((QueueMan.package_progression/QueueMan.package_length)*100)
            
            Logging.New(f"Finished installing ({author}-{name}-{mod_version})")
        
        def UpdateThreadDisplay(self):
            if self.worker:
                self.worker.thread_display_update.emit(
                    self.worker_index,
                    self.download_data['author'],
                    self.download_data['name'],
                    self.download_data['version']
                )
            #if callable(self.thread_display_method): self.thread_display_method(self.worker_index,self.download_data['author'],self.download_data['name'],self.download_data['version'])

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
            if self.worker:
                self.worker.progress_output.emit(self.worker_index,value)
            #if self.signals:
            #    self.signals.progress.emit(self.worker_index, value)
            #if callable(self.emit_method): self.emit_method(self.worker_index,value)