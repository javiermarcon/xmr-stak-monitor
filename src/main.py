#! /usr/bin/env python

import configparser #ConfigParser
import getopt
import logging
import os
from safe_schedule import SafeScheduler
import string
import sys
import time

__version__ = '0.0.1'

from monitor import job

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
        configdefault = { "DEFAULT": {
            "xmr_service": "xmr-stak", # xmr-stak service running
            "xmr_url": "http://127.0.0.1:80",
            "nssm_exe": "../../nssm-2.24/win64/nssm.exe", # nssm executable
        }}

        msg = ""

        logger = logging.getLogger('xmr-stak-monitor')
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
        #cp = ConfigParser.ConfigParser()
        cp = configparser.ConfigParser()
        cp._sections = configdefault
        cp.read(file_ini)

        options = cp._sections
        #print(options)

        scheduler = SafeScheduler()
        scheduler.every(5).minutes.do(job, options["DEFAULT"])
        while True:
            scheduler.run_pending()
            time.sleep(30)

    # argument errors
    except getopt.GetoptError:
        usage()

    # config errors
    except ConfigParser.MissingSectionHeaderError as e:
        msg = "El archivo de configuracion {} es invalido, no contiene secciones. {}".format(file_ini, str(e))
    except ConfigParser.ParsingError as e:
        msg = "El archivo de configuracion {} es invalido, no se puede parsear. {}".format(file_ini, str(e))
    except (ConfigParser.Error, StandardError) as e:
        msg = "Error al leer el archivo de configuracion {}. {}".format(file_ini, str(e))
    except KeyboardInterrupt:
        logger.info("Bye...")
    except Exception as e:
        msg = "Error general []".format(e)
    finally:
        if msg:
            logger.error(msg)
            sys.exit(1)
        sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())