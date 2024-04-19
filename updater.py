import os
import shutil
import time
import subprocess

time.sleep(1)

current_file_loc = os.path.dirname(__file__)

print(current_file_loc)

def migrate_update_files(source,destination):
    print("Moving files...")
    files = os.listdir(source)

    print(source,destination)

    for file in files:
        file_path = os.path.join(source,file)
        destination_path = os.path.join(destination,file)

        if os.path.basename(destination_path) == "_internal":
            for file_internal in os.listdir(file_path):
                f_i_path = f"{source}\\_internal\\{file_internal}"
                print(f_i_path,os.path.join(destination,"_internal",file_internal))
                try:
                    shutil.move(f_i_path,os.path.join(destination,"_internal",file_internal))
                except PermissionError:
                    pass

        try:
            shutil.move(file_path,destination_path)
        except PermissionError:
            pass

#THIS WILL ACT AS IF ITS IN THE _INTERNAL FOLDER
temp_download_folder = os.path.join(current_file_loc,"download_cache")

target_directory = temp_download_folder

for file in os.listdir(temp_download_folder):
    if file.startswith("PBLC"):
        target_directory = os.path.join(temp_download_folder,file)
        break

final_install_path = os.path.dirname(current_file_loc)

if target_directory:
    migrate_update_files(target_directory,final_install_path)

shutil.rmtree(temp_download_folder)
try:
    shutil.rmtree(f"{final_install_path}\\_internal\\_internal")
except FileNotFoundError:
    pass

relaunch_location = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)),"PBLC Update Manager.exe"))

if os.path.exists(relaunch_location):
    subprocess.run(relaunch_location)
else:
    print("Couldn't run EXE")