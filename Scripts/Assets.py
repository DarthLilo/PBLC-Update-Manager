from .Logging import Logging
from .Filetree import Filetree

from enum import Enum

class Assets():

    def __init__(self, assets_folder):
        
        self._assets_folder = assets_folder

        self.asset_dirs = [f"{self._assets_folder}/icons"]

        Filetree.VerifyList(self.asset_dirs)

        Logging.New("Starting assets system...")
    
        self._3270_font = None
    
    def getIcon(icon):


        
        return
    class IconTypes(Enum):
        archive = "icons/archive.png"

    
    
