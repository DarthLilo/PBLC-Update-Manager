from PyQt6.QtCore import QObject, pyqtSignal

import queue, json, threading, time, os, random, traceback
from .Logging import Logging
from .Util import Util
from .Cache import Cache
from .Config import Config
from .Thunderstore import Thunderstore
from .Networking import Networking

class QueueMan():

    max_threads = 6 #int(Config.Read("performance","max_download_threads","value"))
    threads_status = {}
    active_queue = queue.Queue()
    queue_reference = []
    stale_packages = []
    package_length = 0
    package_progression = 0

    def __init__(self):
        QueueMan.max_threads = int(Config.Read("performance","max_download_threads","value"))
        QueueMan.threads_status = {x:"open" for x in range(QueueMan.max_threads)}

    def Debug():

        QueueMan.ClearQueue()
        QueueMan.QueuePackage("DarthLilo","BabyManeater","1.1.2")
        QueueMan.QueuePackage("DarthLilo","LilosScrapExtension","1.4.0")
        threading.Thread(target=QueueMan.Start(),daemon=True)

        return
    
    def GetOpenThread():
        for thread in QueueMan.threads_status:
            if QueueMan.threads_status[thread] == "open":
                return thread
    
    def LockThread(thread):
        QueueMan.threads_status[thread] = "locked"
    
    def UnlockThread(thread):
        QueueMan.threads_status[thread] = "open"
    
    def QueuePackage(author,name,version):
        package = {
            "author":author,
            "name":name,
            "version":version
        }

        #if f"{author}-{name}-{version}" in QueueMan.queue_reference:
        #        return
        
        for entry in QueueMan.queue_reference:
            if str(entry).__contains__(f"{author}-{name}-"):
                local_version = str(entry).split("-")[2]
                if Networking.CompareVersions(version,local_version):
                    Logging.New("Package was already queued, but a newer version was requested, overwriting")
                    QueueMan.stale_packages.append(entry)
                elif Networking.CompareVersions(local_version,version):
                    Logging.New("A newer version of the package was already queued, skipping")
                    return
                else:
                    Logging.New("A package with the same version was already queued, skipping")
                    return
                    

        QueueMan.package_length += 1
        QueueMan.active_queue.put(package)
        QueueMan.queue_reference.append(f"{author}-{name}-{version}")
        Logging.New(f"Queued {package}")

        package_dependencies = Cache.Get(author,name,version)['dependencies']
        if package_dependencies:
            for dependency in package_dependencies:
                if str(dependency).__contains__("BepInEx-BepInExPack-"):
                    continue

                if not dependency in QueueMan.queue_reference:
                    split_dependency = dependency.split("-")
                    QueueMan.QueuePackage(split_dependency[0],split_dependency[1],split_dependency[2])

        return
    
    def QueuePackages(packages):
        """Queues a bunch of packages all at once, should be in list format and each individual entry should follow the standard format"""
        for package in packages:

            #if f"{package['author']}-{package['name']}-{package['version']}" in QueueMan.queue_reference:
            #    continue

            for entry in QueueMan.queue_reference:
                if str(entry).__contains__(f"{package['author']}-{package['name']}-"):
                    local_version = str(entry).split("-")[2]
                    if Networking.CompareVersions(package['version'],local_version):
                        Logging.New("Package was already queued, but a newer version was requested, overwriting")
                        QueueMan.stale_packages.append(entry)
                    elif Networking.CompareVersions(local_version,package['version']):
                        Logging.New("A newer version of the package was already queued, skipping")
                        continue
                    else:
                        Logging.New("A package with the same version was already queued, skipping")
                        continue

            QueueMan.package_length += 1
            QueueMan.active_queue.put(package)
            QueueMan.queue_reference.append(f"{package['author']}-{package['name']}-{package['version']}")
            Logging.New(f"Queued {package}")

            package_dependencies = Cache.Get(package['author'],package['name'],package['version'])['dependencies']
            if package_dependencies:
                for dependency in package_dependencies:
                    if str(dependency).__contains__("BepInEx-BepInExPack-"):
                        continue

                    if not dependency in QueueMan.queue_reference:
                        split_dependency = dependency.split("-")
                        QueueMan.QueuePackage(split_dependency[0],split_dependency[1],split_dependency[2])
    
    def ClearQueue():
        QueueMan.package_length = 0
        QueueMan.stale_packages.clear()
        QueueMan.queue_reference.clear()
        for tasks in range(QueueMan.active_queue.qsize()):
            task = QueueMan.active_queue.get()
            Logging.New(f"Removed {task} from queue!")

    def Execute(threads,overrides_function=None,update=False,emit_method=None,thread_display_method=None,close_download_method=None,loading_screen_method=None,set_global_percent_method=None,finish_func=None):
        active_threads = []
        for i in range(min(threads,QueueMan.package_length)):
            open_thread = QueueMan.GetOpenThread()
            QueueMan.LockThread(open_thread)
            thread = QueueMan.MultiThreadedDownload(QueueMan.active_queue,open_thread,emit_method,thread_display_method,set_global_percent_method)
            thread.start()
            active_threads.append(thread)
        
        for i in range(threads):
            QueueMan.active_queue.put(None)
        
        for thread in active_threads:
            Logging.New(f"{thread.name} joined into main thread")
            thread.join()
        
        Logging.New("All download threads have finished, starting closing proceedures")

        # ALL CODE RELATED THAT NEEDS TO WAIT UNTIL AFTER AN UPDATE HAS COMPLETED MAY BE RUN HERE

        if callable(overrides_function):
            overrides_function(update,close_download_method,loading_screen_method,finish_func) # execute override function
        elif callable(finish_func):
            finish_func()

    def Start(overrides_function=None,update=False, emit_method=None,thread_display_method=None,close_download_method=None,loading_screen_method=None,set_global_percent_method=None,finish_func=None):
        """Starts the multithreaded download based on current queue, must be setup prior to launching download!
        This should also be run inside of its own thread to prevent program freezes!"""

        threads = int(Config.Read("performance","max_download_threads","value"))

        Logging.New("Starting multithreaded download")
        QueueMan.package_progression = 0
        QueueMan.Execute(threads,overrides_function,update,emit_method,thread_display_method,close_download_method,loading_screen_method,set_global_percent_method,finish_func=finish_func)
        
        return
    
    class MultiThreadedDownload(threading.Thread):
        def __init__(self, queue, thread_index,emit_method,thread_display_method,set_global_percent_method):
            threading.Thread.__init__(self,daemon=True)
            self.queue = queue
            self.thread_index = thread_index
            self._emit_method = emit_method
            self._thread_display_method = thread_display_method
            self._set_global_percent_method = set_global_percent_method
        
        def run(self):
            while True:
                package_data = self.queue.get()

                if package_data == None:
                    self.queue.task_done()
                    return
                
                if package_data in QueueMan.stale_packages:
                    self.queue.task_done()
                    Logging.New(f"Package was stale, skipping {package_data}")
                    return
                
                # DOWNLOADING
                if callable(self._thread_display_method): self._thread_display_method(self.thread_index,package_data['author'],package_data['name'],package_data['version'])
                try:
                    self.download_ts_mod(package_data['author'],package_data['name'],package_data['version'])
                except FileNotFoundError:
                    Logging.New(traceback.format_exc(),'error')
                    QueueMan.UnlockThread(self.thread_index)
                    return


                # CLOSING THREAD
                QueueMan.UnlockThread(self.thread_index)
                QueueMan.package_progression += 1
                if callable(self._set_global_percent_method): self._set_global_percent_method((QueueMan.package_progression/QueueMan.package_length)*100)
                self.queue.task_done()
        
        def download_ts_mod(self,author,name,mod_version):
            if not os.path.exists(Cache.SelectedModpack):
                Logging.New("Please select a modpack first!")
                return
            
            if f"{author}-{name}" in Cache.LoadedMods:
                Logging.New(f"{author}-{name} is already installed, skipping!")
                return
            
            mod_location, author, name, mod_version, mod_files = Thunderstore.Download(author=author,mod=name,mod_version=mod_version,feedback_func=self.UpdatePercentage)
            self.AddPackageFiles(author,name,mod_version,mod_files)
            self.LoadMod(mod_location)

            Logging.New(f"Finished installing [{author}-{name}-{mod_version}]")
            return
        
        def UpdatePercentage(self, value):
            if callable(self._emit_method): self._emit_method(self.thread_index,value)
        
        def LoadMod(self,path):
            full_mod_name = os.path.basename(path).split("-")
            author = full_mod_name[0]
            name = full_mod_name[1]

            new_mod = {
                "json_file": f"{path}/mod.json",
                "icon": f"{path}/icon.png",
                }

            Cache.LoadedMods[f"{author}-{name}"] = new_mod
        
        def AddPackageFiles(self,author,name,mod_version,files):
            target_mod_json = f"{Cache.SelectedModpack}/BepInEx/plugins/{author}-{name}-{mod_version}/mod.json"
            mod_json = {}
            mod_json['author'] = author
            mod_json['name'] = name
            mod_json['mod_version'] = mod_version
            mod_json['enabled'] = True
            mod_json['files'] = files
            mod_json['has_updates'] = False
            mod_json['url'] = f"https://thunderstore.io/c/lethal-company/p/{author}/{name}/"

            Util.WriteJson(target_mod_json,mod_json)
            

    
    # Might have to create special download function in the queue manager to avoid circular imports from modpacks.py, shitty but it is what it is