#coding: cp1252

from cx_Freeze import setup, Executable

from main import __version__

dest_base = "xmr-stak-monitor-{}".format(__version__)

base = None

executables = [Executable("main.py", 
						base=base, 
						icon='monitor.ico')]

packages = ['logging', 'getopt', 'sys', 'string', 
			'datetime', 'requests', 'schedule', 
			'traceback', 'subprocess', 'sys',
			'idna' 
							]
options = {
    'build_exe': {

        'packages':packages,
    },

}

setup(
    name = dest_base,
    options = options,
    version = __version__,
    description = "Monitor de cuelgues de xmr-stak",
    executables = executables
)
