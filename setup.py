# set exe to 1 in util
# python -m venv virtual_python
# virtual_python\Scripts\activate.bat
# pip install cx_Freeze, pygame, numpy, six, pillow, etc
# python setup.py build

import cx_Freeze
import os, sys
import subprocess

os.environ['TCL_LIBRARY'] = r'C:\Program Files\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Program Files\Python36\tcl\tk8.6'

PACKAGES = ['pygame']
installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode('utf-8')
installed_packages = installed_packages.split('\r\n')
EXCLUDES = {pkg.split('==')[0] for pkg in installed_packages if pkg != ''}
EXCLUDES.add('tkinter')
for pkg in PACKAGES:
    if type(pkg) == str: EXCLUDES.remove(pkg)
    else: EXCLUDES.remove(pkg[1])

executables = [cx_Freeze.Executable("main.py", base = "Win32GUI", icon="Icon.ico")]
cx_Freeze.setup(
    name="Thunderstorm",
    description="Ludum Dare 51",
    version = "1.1",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":['images/', 'audio/'],
                           'excludes': EXCLUDES,
                           'optimize': 1}},
    executables = executables

    )