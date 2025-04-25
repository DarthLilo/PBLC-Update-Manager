from .Logging import Logging
from .Filetree import Filetree

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QIcon, QPixmap

from enum import Enum
from PIL import Image, ImageOps, ImageQt
import os, winaccent

class Assets():
    
    asset_folder = ""

    def __init__(self, assets_folder):
        Assets.asset_folder = assets_folder


        self.asset_dirs = [f"{assets_folder}/icons"]

        Filetree.VerifyList(self.asset_dirs)
        Logging.New("Starting assets system...")
    
    def InvertColors(image):
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            rgb_image = Image.merge('RGB', (r,g,b))

            inverted_image = ImageOps.invert(rgb_image)
            r2,g2,b2 = inverted_image.split()
            new_image = Image.merge('RGBA',(r2,g2,b2,a))
        else:
            new_image = ImageOps.invert(image)

        return new_image
    
    def getResource(icon,theme=False):
        try:
            icon_path = f"{Assets.asset_folder}/{icon.value}"
        except AttributeError:
            return f"{Assets.asset_folder}/missing_icon.png"
        
        if not os.path.exists(icon_path):
            Logging.New(f"Unable to find {icon.value}")
            return f"{Assets.asset_folder}/missing_icon.png"

        if theme and winaccent.system_uses_light_theme:
            if icon == Assets.ResourceTypes.loading_screen:
                return f"{Assets.asset_folder}/loading_screen_dark.gif"
            return ImageQt.toqpixmap(Assets.InvertColors(Image.open(icon_path)))

        return icon_path
    
    def getGameCover(game):
        icon_path = f"{Assets.asset_folder}/games/{game}/game_cover.jpg"
        if os.path.exists(icon_path):
            return icon_path
        else:
            return f"{Assets.asset_folder}/missing_icon.png"
    
    def modpackIcon(path):
        if not os.path.exists(path):
            return f"{Assets.asset_folder}/missing_icon.png"
        
        return path
    
    def CropCenter(pixmap, scale_factor=2):
        original_w = pixmap.width()
        original_h = pixmap.height()

        crop_width = int(original_w // scale_factor)
        crop_height = int(original_h // scale_factor)
        
        crop_rect = QRect(
            (original_w - crop_width) // 2,
            (original_h - crop_height) // 2,
            crop_width,
            crop_height
        )

        cropped_pixmap = pixmap.copy(crop_rect)
        scaled_pixmap = cropped_pixmap.scaled(original_w,original_h)
        return scaled_pixmap
    
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
        back_arrow = "icons/arrow_left.png"
        missing = "missing_icon.png"
        
    
    class ResourceTypes(str, Enum):
        lethal_font = "3270-Regular.ttf"
        gradient_overlay = "gradient_overlay.png"
        inactive_thread = "inactive_thread.png"
        app_icon = "pill_bottle.ico"
        loading_screen = "loading_screen.gif"
        missing = "missing_icon.png"
    
    class GameTypes(str, Enum):
        lethal_company = "games/lethal_company.jpg"
        repo = "games/repo.jpg"

    
    
