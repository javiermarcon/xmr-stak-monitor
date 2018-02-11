import locale
import logging
import logging.handlers

def loguear(options):
    logger = logging.getLogger('xmr-stak-monitor')
    logger.setLevel(options["level"])
    enc = locale.getpreferredencoding()
    # si ya tengo un handler porque se lanzo con la config default, lo saco para
    # evitar logging repetido
    if logger.hasHandlers():
        for handler in logger.handlers:
            logger.removeHandler(handler)
    handler = logging.handlers.RotatingFileHandler(
            options["filename"], maxBytes=int(options["max_bytes"]),
            backupCount=int(options["backup_count"]), encoding=enc)
    handler.setLevel(options["level"])
    log_format = '%(asctime)s %(levelname)s \t %(message)s' # %(filename)s'
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = True
    return logger