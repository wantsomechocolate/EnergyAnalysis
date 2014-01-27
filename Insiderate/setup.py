## I stopped using py2exe because it is apparently sparingly maintained
## It also doesn't do everything for you like pyinstaller does.

## Although there was a problem with the default pyinstaller file.py
## So I did pyinstaller --onefile file.py and it was much better.

## So basically, navigate to the directory containing tool.py and run
## pyinstaller tool.py

## This has to be done on a Windows machine to get a windows executable.
## I have not found any tool that will create windows binaries
## while not on windows. 

from distutils.core import setup

import py2exe
import matplotlib

setup(
    console=['tool.py'],
    options={
        'py2exe': {
            'excludes':['Tkconstants','Tkinter','tcl'],
            'includes':['matplotlib.backends.backend_wxagg'],
            }
        },
    data_files=matplotlib.get_py2exe_datafiles(),

)

## Download and install py2exe
## Navigate to the directory with the setup file and tool.py
## Type python setup.py py2exe


## And put a shorcut to the exe in
## C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
## Or wherever your startup folder is. 
