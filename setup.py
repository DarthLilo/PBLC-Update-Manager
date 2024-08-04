from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 
                 'excludes': ["numpy"],
                 'bin_includes':["ctkextensions.py"],
                 'include_files': ["updater.py","assets",("python_install.bat","lib/python_install.bat")]}

base = 'Win32GUI'

executables = [
    Executable('main.py', base=base, target_name = 'PBLC Update Manager',icon='assets/pill_bottle.ico'),
    Executable('main.py', base="console", target_name = 'PBLC Update Manager (CONSOLE)',icon='assets/pill_bottle.ico')
]

setup(name='PBLC Update Manager',
      version = '0.3.3',
      description = 'PBLC Update Manager',
      options = {'build_exe': build_options},
      executables = executables,
      author = "DarthLilo")

# python setup.py build | pipdeptree | pip freeze > requirements.txt