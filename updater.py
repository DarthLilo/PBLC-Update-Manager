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
    delete_list = ["assets","PBLC Update Manager.exe","python3.dll","python310.dll"]
    for item in delete_list:
        if os.path.isdir(os.path.join(current_location,item)):
            try:
                shutil.rmtree(os.path.join(current_location,item))
            except:
                pass
        else:
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
        if os.path.isdir(file):
            file_path = os.path.join(source,file)
            for sub_file in os.listdir(file_path):
                print(f"{file}/{sub_file}")
                sub_file_path = os.path.join(source,file,sub_file)
                sub_destination_path = os.path.join(destination,file,sub_file)
                #print(f"{sub_file_path}\n{sub_destination_path}")
                shutil.move(sub_file_path,sub_destination_path)
        else:
            file_path = os.path.join(source,file)
            destination_path = os.path.join(destination,file)
            print(file)

            #print(f"{file_path}\n{destination_path}")
            shutil.move(file_path,destination_path)

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
    subprocess.Popen(relaunch_location)
else:
    print("Couldn't run EXE")

sys.exit()