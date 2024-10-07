class Maths:
    def DownloadPercent(current, total, as_percentage=False):
        new_progress = round(current/total,2)
        
        if as_percentage:
            return new_progress*100
        
        return new_progress