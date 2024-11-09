import math

class Maths:
    def DownloadPercent(current, total, as_percentage=False):
        new_progress = round(current/total,2)
        
        if as_percentage:
            return new_progress*100
        
        return new_progress
    
    def ConvertSize(size_bytes):
        """Converts bytes to their appropriate readable sizes"""
        if size_bytes == 0:
            return "0B"
        
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)

        return "%s %s" % (s, size_name[i])