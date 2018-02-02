#! /usr/bin/env python

import configparser as cpo #ConfigParser en python 2
import eventlet
import getopt
from loggerfunc import loguear
import os
import sys
import time

__version__ = '0.0.1'

from monitor import job, do_restart

def usage():
    print("""Modo de empleo: python main.py [-h]'
        o bien: python main.py [--help]'
        o bien: python main.py [-i <archivo.ini>]'
        o bien: python main.py [--ini=<archivo.ini>]'
        o bien: python main.py [--ini <archivo.ini>]'

Opciones:'
  -h              Muestra el modo de empleo y opciones del conector.'
  --help          Muestra el modo de empleo y opciones del conector.'
  -i <archivo>    Especifica un archivo ini de configuracion.'
  -ini <archivo>  Especifica un archivo ini de configuracion.'
  -ini=<archivo>  Especifica un archivo ini de configuracion.'
""")

def main():
    try:
        # Default INI file
        file_ini = 'config.ini'

        # default config
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

        msg = ""

        logger = loguear(options["log"])

        # leo argumentos de linea de comandos
        opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "ini="])
        for opt, arg in opts:
            if opt in ('-h', "--help"):
                usage()
            elif opt in ("-i", "--ini"):
                if arg.endswith(".ini"):
                    file_ini = arg
                else:
                    usage()

        # parse ini configuration
        if not os.path.isfile(file_ini):
            msg = "No se encuentra el archivo " + str(file_ini) + ", se carga la configuracion default"
            logger.error(msg)
        cp = cpo.ConfigParser()
        cp._sections = options
        cp.read(file_ini)

        options = cp._sections
        logger = loguear(options["log"])
        while True:
            #scheduler.run_pending()
            job(options["service"], logger)
            time.sleep(int(options["service"]["sleep_time"]))

    # argument errors
    except getopt.GetoptError:
        logger.error("error getopt")
        usage()
    # config errors
    except cpo.MissingSectionHeaderError as e:
        logger.error("error 1")
        msg = "El archivo de configuracion {} es invalido, no contiene secciones. {}".format(file_ini, str(e))
    except cpo.ParsingError as e:
        logger.error("error 2")
        msg = "El archivo de configuracion {} es invalido, no se puede parsear. {}".format(file_ini, str(e))
    except cpo.Error as e:
        logger.error("error 3")
        msg = "Error al leer el archivo de configuracion {}. {}".format(file_ini, str(e))
    # exit
    except KeyboardInterrupt:
        logger.error("error 4")
        logger.info("Bye...")
        logger.error("bye ctrl+c")
    # Timeout del checker
    except eventlet.timeout.Timeout:
        do_restart(options, logger)
    # general exception
    except Exception as e:
        logger.error("error 5")
        msg = "Error general: {}".format(e)
        print(msg)
        logger.error(msg)
    """finally:
        logger.error("finally..")
        if msg:
            print(msg)
            logger.error(msg)
            sys.exit(1)
        sys.exit(0)"""

if __name__ == "__main__":
    sys.exit(main())