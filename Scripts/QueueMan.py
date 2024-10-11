import queue, json, threading, time
from .Logging import Logging
from .Util import Util

class QueueMan:

    max_threads = 6
    threads_status = {x:"open" for x in range(max_threads)}
    active_queue = queue.Queue()
    package_length = 0

    def Debug():

        QueueMan.ClearQueue()
        QueueMan.QueuePackage("1","like","1.0.0")
        QueueMan.QueuePackage("2","ong","1.0.0")
        QueueMan.QueuePackage("3","thats","1.0.0")
        QueueMan.QueuePackage("4","freaky","1.0.0")
        QueueMan.QueuePackage("5","as","1.0.0")
        QueueMan.QueuePackage("6","fuck","1.0.0")
        QueueMan.QueuePackage("7","damn","1.0.0")
        QueueMan.QueuePackage("8","damn","1.0.0")
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
                time.sleep(1)
                Logging.New(json.dumps(package_data,indent=4))


                # CLOSING THREAD
                QueueMan.UnlockThread(self.thread_index)
                self.queue.task_done()
    
    # Might have to create special download function in the queue manager to avoid circular imports from modpacks.py, shitty but it is what it is