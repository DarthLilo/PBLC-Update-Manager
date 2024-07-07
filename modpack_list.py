import json, os

def open_json(path):
    with open(path, 'r') as json_opener:
        json_data = json_opener.read()
    json_data = json.loads(json_data)

    return json_data

def parse_update(data, version):

    mods = {}
    for instruction in data:
        if instruction.startswith("url_add_mod"):
            mod_data = instruction.split("|")
            mods[f"{mod_data[2]}_{mod_data[1]}"] = {}
            mods[f"{mod_data[2]}_{mod_data[1]}"]['version'] = mod_data[3]
            mods[f"{mod_data[2]}_{mod_data[1]}"]['name'] = mod_data[2]
            mods[f"{mod_data[2]}_{mod_data[1]}"]['author'] = mod_data[1]

    sorted_mod_keys = sorted(mods.keys(),key=lambda x: x.lower())

    sorted_mods = {}
    for key in sorted_mod_keys:
        sorted_mods[key] = mods[key]

    return sorted_mods

def write_update_log(update_file,log):
    with open(update_file,'a') as updatelog:
        updatelog.write(log)

def create_update_log(new_update,new_mods):
    changelog=[f"# v{new_update} Mods"]


    # New mods

    if len(new_mods) > 0:
        for mod in new_mods:
            changelog.append(f"- **{new_mods[mod]['name']}** ({new_mods[mod]['version']})")
    else:
        changelog.append("- No new mods were added")


    return "\n".join(changelog)

def generate_mods_list(update):
    """Give the version number of the update you wish to create a mods list for"""
    
    update_path = f"update_files/{update}.json"

    # Filepath catch
    if (not os.path.exists(update_path)):
        print("Please enter a valid update!")
        return
    
    # Create changelogs folder
    if not os.path.exists("modlists"):
        os.mkdir("modlists")

    # Delete existing changelog

    changelog_file = f"modlists/{update}-MODLIST.md"

    if os.path.exists(changelog_file):
        os.remove(changelog_file)


    current_mods = parse_update(open_json(update_path)['instructions'],update)
    
    write_update_log(changelog_file,create_update_log(update,current_mods))

generate_mods_list("11.0.0")