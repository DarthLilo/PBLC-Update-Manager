import filecmp, os

def compare_installs(install1,install2):
    """Compares two BepInEx installs. Install1 / Install2 should be absolute paths to the BepInEx folder. (C:\\Users\\NAME\\...\\Lethal Company\\BepInEx)"""
    install1_list = []
    install2_list = []
    missing_files = []
    mismatched_files = []

    if not os.path.exists(install1) or not os.path.exists(install2):
        print("INVALID INSTALL FILE, PLEASE CHECK THE PATH YOU ENTERED")
        return

    for root,dirs,files in os.walk(install1):
        for file in files:
            install1_list.append(os.path.join(root,file))
    
    for root,dirs,files in os.walk(install2):
        for file in files:
            install2_list.append(os.path.join(root,file))

    if len(install1_list) > len(install2_list):
        longer_install = (install1_list,install1)
        shorter_install = (install2_list,install2)
    else:
        longer_install = (install2_list,install2)
        shorter_install = (install1_list,install1)

    for i in range(len(longer_install[0])):

        my_file = longer_install[0][i]
        rel_file = os.path.relpath(longer_install[0][i],longer_install[1])
        their_file = os.path.join(shorter_install[1],rel_file)

        print(f"Checking {rel_file}...")

        if not os.path.exists(their_file):
            missing_files.append(rel_file)
            continue

        if not filecmp.cmp(my_file,their_file,shallow=False):
            mismatched_files.append(rel_file)
    
    print(f"These files are missing from {shorter_install[1]}:\n{missing_files}")
    print(f"These files are mismatched across versions:\n{mismatched_files}")
    return

    


my_lethal = "E:\\Program Files (x86)\\Steam\\steamapps\\common\\Lethal Company\\BepInEx"
exo_lethal = "C:\\Users\\darth\\Desktop\\exo\\BepInEx"

compare_installs(my_lethal,exo_lethal)