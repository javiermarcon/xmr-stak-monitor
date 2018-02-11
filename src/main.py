#! /usr/bin/env python
from config import get_default_options, load_config
import eventlet
import getopt
from loggerfunc import loguear
from monitor import job, do_restart, make_paths_and_urls
import sys
import time

__version__ = '0.0.1'

def usage():
    print("""Modo de empleo: python main.py [-h]'
        o bien: python main.py [--help]'
        o bien: python main.py [-c <archivo.ini>]'
        o bien: python main.py [--config=<archivo.ini>]'
        o bien: python main.py [--config <archivo.ini>]'

Opciones:'
  -h              Muestra el modo de empleo y opciones del conector.'
  --help          Muestra el modo de empleo y opciones del conector.'
  -d <archivo>    Especifica un archivo ini de configuracion.'
  -config <archivo>  Especifica un archivo ini de configuracion.'
  -config=<archivo>  Especifica un archivo ini de configuracion.'
""")

def main():
    try:
        # Default INI file
        file_config = 'config.json'

        options = get_default_options()
        msg = ""
        logger = loguear(options["log"])

        # leo argumentos de linea de comandos
        opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "ini="])
        for opt, arg in opts:
            if opt in ('-h', "--help"):
                usage()
            elif opt in ("-c", "--config"):
                file_config = arg
        options = load_config(file_config, logger)
        logger = loguear(options["log"])
        (nspath, urls) = make_paths_and_urls(options)
        while True:
            #scheduler.run_pending()
            job(urls, nspath, int(options["common"]["page_timeout"]), logger)
            time.sleep(int(options["common"]["sleep_time"]))

    # argument errors
    except getopt.GetoptError:
        usage()
    # config error
    except ValueError as e:
        msg = "Error al leer el archivo de configuracion {}. {}".format(file_config, str(e))
        logger.error(msg)
    # exit
    except KeyboardInterrupt:
        logger.info("bye ctrl+c")
    # Timeout del checker
    except eventlet.timeout.Timeout:
        do_restart(options, logger)
    # general exception
    except Exception as e:
        msg = "Error general: {}".format(e)
        logger.error(msg)

if __name__ == "__main__":
    sys.exit(main())