import os, json

def open_json(path):
    with open(path, 'r') as json_opener:
        json_data = json_opener.read()
    json_data = json.loads(json_data)

    return json_data
    
tempthing = {}

def log_version(install1, install2):
    """Compares two BepInEx installs. Install1 / Install2 should be absolute paths to the BepInEx folder. (C:\\Users\\NAME\\...\\Lethal Company\\BepInEx)"""
    install1_list = []

    finished_files = []

    install1_data = open_json(install1)
    install2_data = open_json(install2)

    for entry in install1_data:
        if entry in finished_files: return

        if entry in install2_data:
            if install2_data[entry] != install1_data[entry]:
                finished_files.append(entry)
                print(f"{entry} does not match!")
        else:
            print(f"{entry} is missing from one install!")
    
    for entry in install2_data:
        if entry in finished_files: return

        if entry in install1_data:
            if install2_data[entry] != install1_data[entry]:
                finished_files.append(entry)
                print(f"{entry} does not match!")
        else:
            print(f"{entry} is missing from one install!")

    return

    


my_lethal = "E:\\Program Files (x86)\\Steam\\steamapps\\common\\Lethal Company\\BepInEx"

log_version(f"{os.path.dirname(__file__)}\\output.json",f"{os.path.dirname(__file__)}\\output_quinn.json")