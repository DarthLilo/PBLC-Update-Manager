import os

from .Util import Util

class Game:

    game_id = None
    steam_id = None
    package_index = None
    package_cache = None
    ts_url_prefix = None
    config_value = None
    data_library = {}
    main_modpack = None
    main_modpack_author = None
    main_modpack_name = None
    

    def __init__(self, games_folder):

        for file in os.listdir(games_folder):
            if os.path.isdir(os.path.join(games_folder,file)):
                game_json = os.path.join(games_folder,file,"game.json")
                if os.path.exists(game_json):
                    Game.data_library[file] = Util.OpenJson(game_json)

    def SelectGame(data):
        Game.game_id = data["game_id"]
        Game._LoadGameData()
    
    def _LoadGameData():
        game_id = Game.game_id
        
        cur_game = Game.data_library[game_id]

        Game.package_index = cur_game["package_index"]
        Game.package_cache = cur_game["package_cache"]
        Game.ts_url_prefix = cur_game["ts_url_prefix"]
        Game.config_value = cur_game["config_value"]
        Game.steam_id = cur_game["steam_id"]
        Game.main_modpack = cur_game["main_modpack"]
        Game.main_modpack_author = cur_game["main_modpack_author"]
        Game.main_modpack_name = cur_game["main_modpack_name"]