import os
import shutil
import time
import subprocess
import sys

time.sleep(1)


def getCurrentPathLoc():

    if getattr(sys,'frozen',False):
        cur_directory = os.path.dirname(sys.executable)
    else:
        cur_directory = os.path.dirname(__file__)
    
    return cur_directory

def clean_old_version():
    current_location = getCurrentPathLoc()
    delete_list = ["assets/3270-Regular.ttf","assets/lethal_art.png","PBLC Update Manager.exe","assets/pill_bottle.ico","assets/missing_icon.png","assets/refresh.png","assets/trash_can.png","assets/website.png","python3.dll","python310.dll"]
    for item in delete_list:
        try:
            os.remove(os.path.join(current_location,item))
            print(f"Removed {item}")
        except:
            pass
    shutil.rmtree(os.path.join(current_location,"lib"))
    print("Cleaned library files")

def migrate_update_files(source,destination):
    print("Moving files...")
    files = os.listdir(source)

    print(source,destination)

    for file in files:
        file_path = os.path.join(source,file)
        destination_path = os.path.join(destination,file)
        print(file)

        #if os.path.basename(destination_path) == "_internal":
        #    for file_internal in os.listdir(file_path):
        #        f_i_path = f"{source}\\_internal\\{file_internal}"
        #        print(f_i_path,os.path.join(destination,"_internal",file_internal))
        #        try:
        #            shutil.move(f_i_path,os.path.join(destination,"_internal",file_internal))
        #        except PermissionError:
        #            pass

        #try:
        shutil.move(file_path,destination_path)
        #except:
        #    pass

#THIS WILL ACT AS IF ITS IN THE _INTERNAL FOLDER
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
    subprocess.run(relaunch_location)
else:
    print("Couldn't run EXE")