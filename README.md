![PBLC Update Manager Logo](https://i.imgur.com/nFTaAqb.png)
# PBLC Update Manager    ![GitHub all releases](https://img.shields.io/github/downloads/DarthLilo/PBLC-Update-Manager/total?color=blue)

This mod manager is designed to be an alternative solution to popular mod management softwares while providing the user with a clean and fluid experience. Both modpack users and developers will be easily able to install and set up mods for Lethal Company

<br/>

# Features

* Multiple modpack support
* Package caching for quick re-downloads
* Online modpack linking for easy install with friends
* A quick and responsive UI
* Extremely fast download times with multithreading

# Building
First you will want to setup a local copy of the repository:
* Download / Clone the repository
* Start a Python environment in the project root folder or open the project with a code editor with one built in. (VSCode)
* Run this command to install all required libraries ``pip install -r requirements.txt``
  
To actually build it into an executable, you will need to install [cx_Freeze](https://pypi.org/project/cx-Freeze/).
* After installing cx_Freeze run this command ``python setup.py build``
* It will output the finished executable to the "build" folder
