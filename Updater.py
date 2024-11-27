import os, sys, shutil, subprocess, traceback

def getCurrentPathLoc():

    if getattr(sys,'frozen',False):
        cur_directory = os.path.dirname(sys.executable)
    else:
        cur_directory = os.path.dirname(__file__)
    
    return cur_directory

def clean_old_version():
    current_location = getCurrentPathLoc()
    delete_list = ["ProgramAssets","PBLC Update Manager.exe","PBLC Update Manager Console.exe"]
    for item in delete_list:
        if os.path.isdir(os.path.join(current_location,item)):
            try:
                shutil.rmtree(os.path.join(current_location,item))
                print(f"Removed {item}")
            except:
                print(f"Unable to remove {item}")
                print(traceback.format_exc())
        else:
            try:
                os.remove(os.path.join(current_location,item))
                print(f"Removed {item}")
            except:
                print(f"Unable to remove {item}")
                print(traceback.format_exc())
    

def migrate_update_files(source,destination):
    print("Moving files...")
    files = os.listdir(source)

    print(source,destination)

    for root, dirs, files in os.walk(source):
        for file in files:
            rel_path = os.path.relpath(root,source)
            dest_dir_path = os.path.join(destination,rel_path)

            os.makedirs(dest_dir_path, exist_ok=True)

            src_path = os.path.join(root,file)
            final_path = os.path.join(dest_dir_path,file)

            try:
                shutil.move(src_path,final_path)
            except PermissionError:
                print(f"PermissionError: Couldn't move {src_path}, skipping...")
            except Exception as e:
                print(f"Unknown error when handling {src_path}")
                print(traceback.format_exc())

temp_download_folder = os.path.join(getCurrentPathLoc(),"download_cache")
target_directory = temp_download_folder

for file in os.listdir(temp_download_folder):
    if file.startswith("PBLC"):
        target_directory = os.path.join(temp_download_folder,file)
        break

if target_directory:
    clean_old_version()
    migrate_update_files(target_directory,getCurrentPathLoc())

shutil.rmtree(temp_download_folder)

relaunch_location = os.path.normpath(os.path.join(getCurrentPathLoc(),"PBLC Update Manager.exe"))

if os.path.exists(relaunch_location):
    print("Attempting EXE Launch")
    subprocess.Popen(relaunch_location)
else:
    print("Couldn't run EXE")

sys.exit()