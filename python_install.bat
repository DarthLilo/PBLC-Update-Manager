@echo Starting python install...

set PYTHON_VERSION=3.12.4
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe

@echo Downloading...

curl -o python-%PYTHON_VERSION%-amd64.exe %PYTHON_URL%

@echo Be sure to accept the permissions prompt!

python-%PYTHON_VERSION%-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

setx PATH "%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python%PYTHON_VERSION%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python%PYTHON_VERSION%\Scripts" /M

@echo Python install completed

del python-%PYTHON_VERSION%-amd64.exe

python --version

timeout /t 5 /nobreak >nul

@echo Finished installing python, reboot PBLC Update Manager.