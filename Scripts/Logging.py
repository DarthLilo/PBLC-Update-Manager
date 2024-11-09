from .Time import Time
import os, threading

class Logging():

    LoggingFolder = ""
    CurrentLog = None
    PBLCVersion = ""

    def __init__(self, LoggingFolder,PBLCVersion):
        Logging.LoggingFolder = LoggingFolder
        Logging.PBLCVersion = PBLCVersion

        Logging.Start()
        return
    
    def Start():
        
        start_date = Time.CurrentDate()
        log_count = 1

        for file in os.listdir(Logging.LoggingFolder):
            if file.startswith(start_date):
                log_count += 1
        
        Logging.CurrentLog = f"{Logging.LoggingFolder}/{start_date}-{log_count}.pblc_log"
        Logging.New("Initialized logging system","startup")

        return
    
    def New(message,log_type='info'):
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

        current_thread = threading.current_thread().name

        log_entry = f"[{Time.CurrentTime()}] {log_types[log_type]} [{current_thread}] {message}"

        with open(Logging.CurrentLog, 'a') as log_write:
            log_write.write(log_entry+"\n")
        
        print(log_entry)
        return
    
    def Close():
        current_thread = threading.current_thread().name
        log_entry = f"[{Time.CurrentTime()}] [END] [{current_thread}] PBLC Update Manager - [{Logging.PBLCVersion}] is closing!"
        with open(Logging.CurrentLog,'a') as log_write:
            log_write.write(log_entry)
        print(log_entry)
        return
