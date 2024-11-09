import os, sys, shutil, subprocess

def getCurrentPathLoc():

    if getattr(sys,'frozen',False):
        cur_directory = os.path.dirname(sys.executable)
    else:
        cur_directory = os.path.dirname(__file__)
    
    return cur_directory

def clean_old_version():
    current_location = getCurrentPathLoc()
    delete_list = ["ProgramAssets","PBLC Update Manager.exe","PBLC Update Manager Console.exe","python3.dll","python310.dll"]
    for item in delete_list:
        if os.path.isdir(os.path.join(current_location,item)):
            try:
                shutil.rmtree(os.path.join(current_location,item))
                print(f"Removed {item}")
            except:
                print(f"Unable to remove {item}")
        else:
            try:
                os.remove(os.path.join(current_location,item))
                print(f"Removed {item}")
            except:
                print(f"Unable to remove {item}")
    

def migrate_update_files(source,destination):
    print("Moving files...")
    files = os.listdir(source)

    print(source,destination)

    for file in files:
        if os.path.isdir(file):
            file_path = os.path.join(source,file)
            for sub_file in os.listdir(file_path):
                sub_file_path = os.path.join(source,file,sub_file)
                sub_destination_path = os.path.join(destination,file,sub_file)
                print(sub_file_path)
                try:
                    shutil.move(sub_file_path,sub_destination_path)
                    print(f"Copied {sub_file}")
                except PermissionError:
                    print(f"Permission error when copying {sub_file}")
                    continue
        else:
            file_path = os.path.join(source,file)
            destination_path = os.path.join(destination,file)
            try:
                shutil.move(file_path,destination_path)
            except PermissionError:
                continue

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