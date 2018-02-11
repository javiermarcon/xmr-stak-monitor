import json
import os

# default config
def get_default_options():
    options = { "service": {
        "xmr_service": "xmr-stak", # xmr-stak service running
        "xmr_url": "http://127.0.0.1:80",
        "nssm_exe": "../../nssm-2.24/win64/nssm.exe", # nssm executable
        "sleep_time": 300,
        "page_timeout": 20
        },
        "log":{
            "filename": "monitor.log",
            "level": "DEBUG",
            "max_bytes": 500000000,
            "backup_count": 5
        }
    }
    return options

def load_config(file_config, logger):
    # parse ini configuration
    if os.path.isfile(file_config):
        with open(file_config) as f:
            cont = f.read()
            options = json.loads(cont)
    else:
        options = get_default_options()
        f = open(file_config, "w+")
        d = json.dumps(options, sort_keys=True, indent=4)
        f.write(d)
        f.close()
        msg = "No se encuentra el archivo {}, ".format(file_config)
        msg += "se carga la configuracion default "
        msg += "y se crea un archivo con dicha configuracion."
        logger.error(msg)
    return options