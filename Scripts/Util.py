import winreg

class Util:
    def ReadReg(ep, p = r"", k = ''):
        try:
            key = winreg.OpenKeyEx(ep, p)
            value = winreg.QueryValueEx(key,k)
            if key:
                winreg.CloseKey(key)
            return value[0]
        except Exception as e:
            return None