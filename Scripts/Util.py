import winreg, traceback, json, validators
from urllib import request
from .Logging import Logging

class Util:
    def ReadReg(ep, p = r"", k = ''):
        try:
            key = winreg.OpenKeyEx(ep, p)
            value = winreg.QueryValueEx(key,k)
            if key:
                winreg.CloseKey(key)
            return value[0]
        except FileNotFoundError as e:
            Logging.New(traceback.format_exc(),'error')
            return "Check32Bit"
        except Exception as e:
            Logging.New(traceback.format_exc(),'error')
            return None
        
    def OpenJson(path):
        with open(path, 'r') as json_opener:
            json_data = json_opener.read()
        json_data = json.loads(json_data)

        return json_data
    
    def WriteJson(path,data):
        with open(path, "w") as json_writer:
            json_writer.write(json.dumps(data,indent=4))
    
    def UrlPathDecoder(path):

        if validators.url(path):
            return json.loads(request.urlopen(path).read().decode())
        
        return Util.OpenJson(path)