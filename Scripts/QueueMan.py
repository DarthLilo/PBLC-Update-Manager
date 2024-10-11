import queue, json, threading, time, os
from .Logging import Logging
from .Util import Util
from .Cache import Cache
from .Thunderstore import Thunderstore
from .Modpacks import Modpacks

class QueueMan:

    max_threads = 6
    threads_status = {x:"open" for x in range(max_threads)}
    active_queue = queue.Queue()
    queue_reference = []
    package_length = 0

    def Debug():

        QueueMan.ClearQueue()
        QueueMan.QueuePackage("DarthLilo","MagnetLock","1.2.0")
        QueueMan.QueuePackage("DarthLilo","LevelMusicLib","1.0.2")
        QueueMan.QueuePackage("DarthLilo","WhoVoted","1.0.2")
        QueueMan.QueuePackage("DarthLilo","BabyManeater","1.1.2")
        QueueMan.QueuePackage("DarthLilo","LilosScrapExtension","1.4.0")
        QueueMan.QueuePackage("DarthLilo","SkinnedRendererPatch","1.1.3")
        QueueMan.QueuePackage("AinaVT","LethalConfig","1.4.3")
        QueueMan.QueuePackage("IAmBatby","LethalLevelLoader","1.3.10")
        QueueMan.QueuePackage("Evaisa","LethalLib","0.16.1")
        QueueMan.QueuePackage("Evaisa","FixPluginTypesSerialization","1.1.1")
        QueueMan.QueuePackage("MaxWasUnavailable","LethalModDataLib","1.2.2")
        QueueMan.QueuePackage("Evaisa","HookGenPatcher","0.0.5")
        #threading.Thread(target=QueueMan.Start(),daemon=True)
        Logging.New(QueueMan.active_queue)

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

        QueueMan.package_length += 1
        QueueMan.active_queue.put(package)
        Logging.New(f"Queued {package}")

        return
    
    def QueuePackages(packages):
        """Queues a bunch of packages all at once, should be in list format and each individual entry should follow the standard format"""
        for package in packages:
            QueueMan.package_length += 1
            QueueMan.active_queue.put(package)
            Logging.New(f"Queued {package}")
    
    def ClearQueue():
        for tasks in range(QueueMan.active_queue.qsize()):
            task = QueueMan.active_queue.get()
            Logging.New(f"Removed {task} from queue!")

    def Execute(threads=max_threads):
        active_threads = []
        for i in range(min(threads,QueueMan.package_length)):
            open_thread = QueueMan.GetOpenThread()
            QueueMan.LockThread(open_thread)
            thread = QueueMan.MultiThreadedDownload(QueueMan.active_queue,open_thread)
            thread.start()
            active_threads.append(thread)
        
        for i in range(threads):
            QueueMan.active_queue.put(None)
        
        for thread in active_threads:
            Logging.New(f"{thread.name} joined into main thread")
            thread.join()
        
        Logging.New("All download threads have finished, starting closing proceedures")

        # ALL CODE RELATED THAT NEEDS TO WAIT UNTIL AFTER AN UPDATE HAS COMPLETED MAY BE RUN HERE

        print('oh shit bitch')
        Logging.New("NANANANA BOOOO BOOOOOOOO")

    def Start(threads=max_threads):
        """Starts the multithreaded download based on current queue, must be setup prior to launching download!
        This should also be run inside of its own thread to prevent program freezes!"""

        download_thread = threading.Thread(target=lambda threads = threads:QueueMan.Execute(threads),daemon=True)
        Logging.New("Starting multithreaded download")
        download_thread.start()
        
        return
    
    class MultiThreadedDownload(threading.Thread):
        def __init__(self, queue, thread_index):
            threading.Thread.__init__(self,daemon=True)
            self.queue = queue
            self.thread_index = thread_index
        
        def run(self):
            while True:
                package_data = self.queue.get()

                if package_data == None:
                    self.queue.task_done()
                    return
                
                # DOWNLOADING
                self.download_ts_mod(package_data['author'],package_data['name'],package_data['version'])


                # CLOSING THREAD
                QueueMan.UnlockThread(self.thread_index)
                self.queue.task_done()
        
        def download_ts_mod(self,author,name,mod_version):
            if not os.path.exists(Cache.SelectedModpack):
                Logging.New("Please select a modpack first!")
                return
            
            if Modpacks.Mods.Installed(author,name):
                Logging.New(f"{author}-{name} is already installed, skipping!")
                return
            
            mod_location, author, name, mod_version, mod_files = Thunderstore.Download(author=author,mod=name,mod_version=mod_version)
            Modpacks.Mods.AddPackageFiles(author,name,mod_version,mod_files)
            Modpacks.Mods.LoadMod(mod_location)

            Logging.New(f"Finished installing [{author}-{name}-{mod_version}]")
            return
            

    
    # Might have to create special download function in the queue manager to avoid circular imports from modpacks.py, shitty but it is what it is