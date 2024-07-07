import json,os

patch_path = "patch_instructions.json"

def open_json(path):
    with open(path, 'r') as json_opener:
        json_data = json_opener.read()
    json_data = json.loads(json_data)

    return json_data

def parse_patches(update,beta=False):
    patches = open_json(patch_path)
    additions = {}
    removals = {}

    if beta: 
        return

    if update in patches:
        for patch in patches[update]['release']:
            for instruction in patches[update]['release'][patch]:
                mod_data = instruction.split("|")
                if instruction.startswith("url_add_mod"):
                    additions[f"{mod_data[1]}_{mod_data[2]}"] = {}
                    additions[f"{mod_data[1]}_{mod_data[2]}"]['version'] = mod_data[3]
                    additions[f"{mod_data[1]}_{mod_data[2]}"]['name'] = mod_data[2]
                    additions[f"{mod_data[1]}_{mod_data[2]}"]['author'] = mod_data[1]
                    if f"{mod_data[1]}_{mod_data[2]}" in removals:
                        del removals[f"{mod_data[1]}_{mod_data[2]}"]
                elif instruction.startswith("delete_mod"):
                    removals[f"{mod_data[1]}_{mod_data[2]}"] = {}
                    removals[f"{mod_data[1]}_{mod_data[2]}"]['name'] = mod_data[2]
                    removals[f"{mod_data[1]}_{mod_data[2]}"]['author'] = mod_data[1]
                    if f"{mod_data[1]}_{mod_data[2]}" in additions:
                        del additions[f"{mod_data[1]}_{mod_data[2]}"]

    return additions, removals

def parse_update(data, version):

    additions, removals = parse_patches(version)

    mods = {}
    for instruction in data:
        if instruction.startswith("url_add_mod"):
            mod_data = instruction.split("|")
            mods[f"{mod_data[1]}_{mod_data[2]}"] = {}
            mods[f"{mod_data[1]}_{mod_data[2]}"]['version'] = mod_data[3]
            mods[f"{mod_data[1]}_{mod_data[2]}"]['name'] = mod_data[2]
            mods[f"{mod_data[1]}_{mod_data[2]}"]['author'] = mod_data[1]
    
    for addition in additions:
        mods[addition] = additions[addition]
    
    for removal in removals:
        try:
            del mods[removal]
        except KeyError:
            pass
    
    return mods

def write_changelog(changelog_file,log):
    with open(changelog_file,'a') as changelog:
        changelog.write(log)

def create_changelog(new_update,new_mods,updated_mods,deleted_mods):
    changelog=[f"# v{new_update} Changelog"]


    # New mods

    changelog.append("## Additions")

    if len(new_mods) > 0:
        for mod in new_mods:
            changelog.append(f"- Added **{new_mods[mod]['name']}** ({new_mods[mod]['version']})")
    else:
        changelog.append("- No new mods were added")
    
    # Updated mods

    changelog.append("## Updated")

    if len(updated_mods) > 0:
        for mod in updated_mods:
            changelog.append(f"- Updated **{updated_mods[mod]['name']}** to **{updated_mods[mod]['version']}**")
    else:
        changelog.append("- No mods were updated")

    # Deleted mods

    changelog.append("## Removed")

    if len(deleted_mods) > 0:
        for mod in deleted_mods:
            changelog.append(f"- Removed **{deleted_mods[mod]['name']}**")
    else:
        changelog.append("- No mods were removed")






    return "\n".join(changelog)

def compare_update_files(old_update="",new_update="",old_update_is_beta=False,new_update_is_beta=False):
    """Input in the the new and old update filepaths and it will generate a changelog file"""

    # Validate updates
    old_update_path = f"update_files/{old_update}.json" if not old_update_is_beta else f"update_files/{old_update}_beta.json"
    new_update_path = f"update_files/{old_update}.json" if not new_update_is_beta else f"update_files/{new_update}_beta.json"

    # Validate patch instructions
    if not os.path.exists(patch_path):
        print("Please make sure the patch instructions file is present!")
        return

    # Filepath catch
    if (not os.path.exists(old_update_path)) or (not os.path.exists(new_update_path)):
        print("Please enter valid updates!")
        return
    
    # Create changelogs folder
    if not os.path.exists("update_changelogs"):
        os.mkdir("update_changelogs")
    
    # Delete existing changelog

    changelog_file = f"update_changelogs/{old_update}-{new_update}-CHANGELOG.md"

    if os.path.exists(changelog_file):
        os.remove(changelog_file)

    

    old_mods = parse_update(open_json(old_update_path)['instructions'],old_update)
    new_mods = parse_update(open_json(new_update_path)['instructions'],new_update)

    updated_mods = {}
    deleted_mods = {}

    for mod in old_mods:
        if mod in new_mods:

            if old_mods[mod]['version'] != new_mods[mod]['version']: #VERSION CHANGED
                updated_mods[mod] = new_mods[mod]
                del new_mods[mod]

            elif old_mods[mod]['version'] == new_mods[mod]['version']: #MOD UNCHANGED
                del new_mods[mod]
        else:
            deleted_mods[mod] = old_mods[mod]
    
    write_changelog(changelog_file,create_changelog(new_update,new_mods,updated_mods,deleted_mods))

    return

compare_update_files("10.0.0","11.0.0")