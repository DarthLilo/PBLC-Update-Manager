from .Logging import Logging
from .Filetree import Filetree

from enum import Enum

import os

class Assets():
    
    asset_folder = ""

    def __init__(self, assets_folder):
        Assets.asset_folder = assets_folder


        self.asset_dirs = [f"{assets_folder}/icons"]

        Filetree.VerifyList(self.asset_dirs)
        Logging.New("Starting assets system...")
    
    def getResource(icon):
        icon_path = f"{Assets.asset_folder}/{icon.value}"
        if not os.path.exists(icon_path):
            Logging.New(f"Unable to find {icon.value}")
            return f"{Assets.asset_folder}/missing_icon.png"

        return icon_path
    
    def modpackIcon(path):
        if not os.path.exists(path):
            return f"{Assets.asset_folder}/missing_icon.png"
        
        return path
    
    class IconTypes(str,Enum):
        archive = "icons/archive.png"
        arrow_right_up = "icons/arrow_right_up.png"
        checklist = "icons/checklist.png"
        checkmark = "icons/checkmark.png"
        cross = "icons/cross.png"
        download = "icons/download.png"
        file = "icons/file.png"
        folder = "icons/folder.png"
        info = "icons/info.png"
        play = "icons/play.png"
        plus = "icons/plus.png"
        refresh = "icons/refresh.png"
        save = "icons/save.png"
        trash_can = "icons/trash_can.png"
        uninstall = "icons/uninstall.png"
        link = "icons/website.png"
        edit = "icons/edit.png"
        missing = "missing_icon.png"
    
    class ResourceTypes(str, Enum):
        lethal_font = "3270-Regular.ttf"
        gradient_overlay = "gradient_overlay.png"
        inactive_thread = "inactive_thread.png"
        app_icon = "pill_bottle.ico"
        loading_screen = "loading_screen.gif"
        missing = "missing_icon.png"

    
    
