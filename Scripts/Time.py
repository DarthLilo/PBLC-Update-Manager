from datetime import datetime

class Time():

    def Now():
        return datetime.timestamp(datetime.now())
    
    def DateNow():
        return datetime.now()
    
    def TimePassed(start, end):
        start_time = datetime.fromtimestamp(start)
        end_time = datetime.fromtimestamp(end)

        difference = end_time-start_time
        difference = round(difference.total_seconds())

        hours, remainder = divmod(difference, 3600)
        minutes, seconds = divmod(remainder,60)
        formatted_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
        return formatted_time
    
    def SecondsPassed(start, end):
        start_time = datetime.fromtimestamp(start)
        end_time = datetime.fromtimestamp(end)
        difference = end_time-start_time
        return round(difference.total_seconds())
    
    def CurrentDate():
        return str(datetime.now().strftime("%m-%d-%Y"))
    
    def CurrentTime():
        return str(datetime.now().strftime("%H:%M:%S"))
    
    def IsOlder(local,outwards):
        """Checks if the \"local\" time is older than the \"outwards\" time"""
        return local < outwards