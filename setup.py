from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 
                 'excludes': ["numpy"],
                 'bin_includes':[],
                 'include_files': ["Updater.py","ProgramAssets",("python_install.bat","lib/python_install.bat")]}

executables = [
    Executable('main.py', base='Win32GUI', target_name = 'PBLC Update Manager',icon='ProgramAssets/pill_bottle.ico'),
    Executable('main.py', base='Console', target_name = 'PBLC Update Manager Console',icon='ProgramAssets/pill_bottle.ico')
]

setup(name='PBLC Update Manager',
      version = '1.0.0',
      description = 'PBLC Update Manager',
      options = {'build_exe': build_options},
      executables = executables,
      author = "DarthLilo")

# python setup.py build | pipdeptree | pip freeze > requirements.txt