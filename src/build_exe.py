#coding: cp1252

import sys
from cx_Freeze import setup, Executable

from main import __version__

dest_base = "xmr-stak-monitor-{}".format(__version__)

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [Executable("main.py", 
						base=base, 
						icon='monitor.ico')]

packages = ['logging', 'getopt', 'sys', 'string', 
			'datetime', 'requests', 'schedule', 
			'traceback', 'subprocess', 'sys',
			'idna', 'eventlet', 'os', 'time',
            'locale', 'certifi', 'urllib3', 'greenlet'
							]
options = {
    'build_exe': {
        'packages': packages,
        'include_files': ['config.ini'],
    },

}

setup(
    name = dest_base,
    options = options,
    version = __version__,
    description = "Monitor de cuelgues de xmr-stak",
    executables = executables
)
