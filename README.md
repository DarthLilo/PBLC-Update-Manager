![PBLC Update Manager Logo](https://i.imgur.com/nFTaAqb.png)
# PBLC Update Manager    ![GitHub all releases](https://img.shields.io/github/downloads/DarthLilo/PBLC-Update-Manager/total?color=blue)



This is a simple mod updater to easily have friends update Lethal Company mods while still providing a strong enough modpack backend to allow you to create modpacks for friendgroups easily.

### IMPORTANT
Before reading any further, this program is still in very early development and things are likely to be unstable and or change in the future!

As of right now it isn't possible to easily change which modpack it will download, however, it will be in the future.

<br/>

# Features

* Downloading of main and beta version modpacks
* Built-in program updater
* Add mods by pasting a thunderstore page link
* Toggle, update, and delete installed mods easily
* Export modpacks with all required files with one button
* Send out patches to modpacks so users won't have to redownload massive files
* Easy mod management for pack creators

# Future Plans (?)
  * Multiple Mod Profiles

# Building
First you will want to setup a local copy of the repository:
* Download / Clone the repository
* Start a Python environment in the project root folder or open the project with a code editor with one built in. (VSCode)
* Run this command to install all required libraries ``pip install -r requirements.txt``
  
To actually build it into an executable, you will need to install [cx_Freeze](https://pypi.org/project/cx-Freeze/).
* After installing cx_Freeze run this command ``python setup.py build``
* It will output the finished executable to the "build" folder
