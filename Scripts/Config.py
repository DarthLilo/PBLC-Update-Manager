import os, configobj, traceback
from .Logging import Logging

class Config():

    ConfigFilePath = ""
    Data = None

    def __init__(self, DataFolder):
        Config.ConfigFilePath = f"{DataFolder}/config.ini"
        Logging.New("Starting config system...", 'startup')

        Config.CheckForConfig() # Locate config
        Config.Load() # Load config
        Config.Verify()

        return
    
    def CheckForConfig():
        """Runs a check to see if the config file exists, if not, generate a new one"""

        if not os.path.exists(Config.ConfigFilePath): # Generate a new config if none found
            Logging.New("No config file found, regenerating...")
            Config.Reset()
        
        return
    
    def Load():
        Config.Data = configobj.ConfigObj(Config.ConfigFilePath)

    def Reset():
        """Resets the config to default regardless of whether it exists or not"""

        config = configobj.ConfigObj()
        config.filename = Config.ConfigFilePath
        config.initial_comment = ["PBLC Update Manager Configuration",""]

        settings_library = Config.Library(return_all=True)
        for container in settings_library:
            config[container] = settings_library[container]

        config.write()

        Logging.New("Reset Config")

        return
    
    def Library(container="",setting="",return_all=False):
        """Grabs configs, either the whole library, settings container, or specific setting"""

        settings_library = {

            "general": {
                "lethal_company_path": {
                    "value": "",
                    "default": "",
                    "description": "Overrides the Lethal Company path function and allows the user to set it manually",
                    "type": "folder"
                },
                "auto_download_modpack": {
                    "value": True,
                    "default": True,
                    "description": "Automatically prompts to download the main modpack to avoid user hastle",
                    "type": "bool"
                },
                "major_task_running": {
                    "value": False,
                    "default": False,
                    "description": "",
                    "type": "hidden"
                }

            },
            "performance": {
                "max_download_threads": {
                    "value": 6,
                    "default": 6,
                    "description": "Decides how many threads",
                    "type": "int"
                }
            },
            "advanced": {
                "overrite_protocol_key": {
                    "value": False,
                    "default": False,
                    "description": "Overwrites the shell protocol key for \"ror2mm\" to allow PBLC to work with thunderstore's website, this setting will automatically deactivate after being enabled!",
                    "type": "bool"
                }
            }

        }

        if return_all: return settings_library # Returns the entire library

        elif container and not setting: # Returns an entire config container (General for example)
            return settings_library[container]
        
        elif container and setting: # Returns a config group, not specific values
            return settings_library[container][setting]


        return
    
    def Read(container,setting,target):
        """Returns config data provided the container, value, and target
        
        Valid target options are [\"value\", \"default\", \"description\", \"type\", \"values\"]"""
        
        data = None

        if not target:
            Logging.New("Please specify a valid target when reading config!",'warning')
            return data
        
        try:
            data = Config.Data[container][setting][target]
        except (KeyError) as e:
            Logging.New(traceback.format_exc(),'error')
            Logging.New(f"{container}/{setting}/{target} does not exist!",'warning')
        
        return data
    
    def Write(container,setting,data,game_override_path=False):
        """Writes new data to a config option for future use."""

        if container not in Config.Data:
            Config.Data[container] = Config.Library(container)
        
        if setting not in Config.Data[container]:
            if game_override_path:
                Config.Data[container][setting] = {"value": "", "default": "", "description": "Path to specific game folder, able to be overriden by the user", "type": "folder"}
                print(Config.Data)
            else:
                Config.Data[container][setting] = Config.Library(container,setting)
        
        Config.Data[container][setting]['value'] = data

        Config.Data.write()
    
    def Verify():

        config_library = Config.Library(return_all=True)

        for container in config_library:

            if not container in Config.Data:
                
                Config.Data[container] = config_library[container]
                continue

            for setting in config_library[container]:
                if not setting in Config.Data[container]:
                    Config.Data[container][setting] = config_library[container][setting]
        
        Config.Data.write()

        return

    def Get():
        return Config.Data 