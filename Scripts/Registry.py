import winreg, sys, traceback, ctypes
from .Logging import Logging
from .Config import Config

class Registry:

    def IsAdmin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def RestartAsAdmin():
        if not Registry.IsAdmin():
            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

            if result <= 32:
                Logging.New("Admin permissions were denied, continuing with normal operation")
                return False
            
            sys.exit(0)
        return True

    def GetProtocolHandler():
        """Gets the protocol handler from the regristry"""
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "ror2mm") as key:
                current_handler = winreg.QueryValue(key, r"shell\open\command")
                return current_handler
        except FileNotFoundError:
            return None

    def SetProtocolHandler():
        try:

            try:
                key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "ror2mm", 0, winreg.KEY_WRITE)
            except FileNotFoundError:
                key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "ror2mm")
            
            
            winreg.SetValue(key,r"shell\open\command", winreg.REG_SZ, f'"{sys.executable}" "%1"')
            winreg.SetValue(key, "",winreg.REG_SZ,"URL: PBLC Update Manager Protocol")
            winreg.SetValueEx(key,"URL Protocol",0,winreg.REG_SZ, "")

            winreg.CloseKey(key)
            Logging.New(f"Protocol set to {sys.executable}")

        except Exception as e:
            Logging.New("Error when setting protocol handler")
            Logging.New(traceback.format_exc())

    def EnsureProtocolHandler():
        current_handler = Registry.GetProtocolHandler()

        if current_handler is None or Config.Read("advanced","overrite_protocol_key","value") == "True":
            Logging.New("Setting up protocol handler, this will be removed if R2MM is installed later!")
            perms = Registry.RestartAsAdmin()
            Logging.New(perms)
            if not perms:
                return
            Registry.SetProtocolHandler()
            Config.Write("advanced","overrite_protocol_key","False")
        else:
            Logging.New("Protocal is already registered, skipping...")