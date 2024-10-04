import hashlib, os, json

def sha256sum(filename):
    """Calculate the SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()
    
tempthing = {}

def log_version(install1, output_file):
    """Compares two BepInEx installs. Install1 / Install2 should be absolute paths to the BepInEx folder. (C:\\Users\\NAME\\...\\Lethal Company\\BepInEx)"""
    install1_list = []
    install1 = os.path.normpath(install1)

    if not os.path.exists(install1):
        print(install1)
        print("INVALID PATH!")
        return

    for root,dirs,files in os.walk(install1):
        for file in files:
            install1_list.append(os.path.join(root,file))

    for i in range(len(install1_list)):
        my_file = install1_list[i]

        print(f"Checking {my_file}...")
        try:
            tempthing[os.path.basename(my_file)] = sha256sum(my_file) 
        except PermissionError:
            print(f"PERMISSION DENIED ON FILE {my_file}")
        except AttributeError:
            print(f"UNKNOWN ERROR {my_file}")
    

    with open(output_file, 'w') as write:
        write.write(json.dumps(tempthing,indent=4))
    return

    


my_lethal = "E:\\Program Files (x86)\\Steam\\steamapps\\common\\Lethal Company\\BepInEx"

log_version(f"{input()}\\BepInEx",f"{os.path.dirname(__file__)}\\output.json")