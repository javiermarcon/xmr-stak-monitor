import datetime
import eventlet
import os
import requests
import subprocess

def do_restart(options, logger):
    nspath = os.path.abspath(options["nssm_exe"]).replace('\\', '\\\\')
    cmd = [nspath, "restart", options["xmr_service"]]
    logger.debug("primer call: {}".format(" ".join(cmd)))
    ejecuto(cmd, logger)

def ejecuto(cmd, logger):
    try:
        logger.debug("inicio_exe")
        subprocess.run(cmd, check=False)
        # Para python2 usar subprocess.call(cmd)
        logger.debug("fin exe")
    except Exception as ee:
        logger.debug(ee)

def job(options, logger):
    logger.info("I'm working...")
    url = "{}/h".format(options["xmr_url"])
    pag = get_web_page(url, logger, int(options["page_timeout"]))
    logger.debug("got page")
    if pag["status"] != "OK":
        logger.debug("not ok..")
        logger.warn("page failed at {}.".format(datetime.datetime.now()))
        logger.debug(pag)
        print ("a")
        do_restart(options, logger)
        print("e")
        logger.debug("segundo call")
    else:
        logger.debug("pag ok.")

def get_web_page(url, logger, timeout=10, http_method="GET"):
    """
    gets a web page
    :param url: string with the url to retrieve, for example: https://pepe.com:8000/sarasa
    :param http_method: string with the method to use ("GET" or "POST")
    :return: a dictionary with:
                    state: "ok" or "failure"
					status_code: http response number (200=ok, 404=not found, etc.)
                    content: the web page html content in cas of success or the error in case of error.
    """
    status = "FAILURE"
    status_code = -1
    logger.debug("Inicio Request ({})a {}".format(http_method, url))
    try:
        eventlet.monkey_patch()
        with eventlet.Timeout(10):
            if (http_method.lower().strip() == 'get'):
                resp = requests.get(url, verify=False)
                logger.debug("Fin request Get") 
            else:
                resp = requests.post(url, verify=False)
                logger.debug("Fin Request POST")
            content = resp.content
            status_code = resp.status_code
            if status_code == 200:
                status = "OK"
            logger.debug("status:{} resp_code{}".format(status, status_code))
            return {
                "status": status,
                "status_code": status_code,
                "content": content
                }
    except (Exception, eventlet.timeout.Timeout) as ex:
        logger.error("error trayendo web page")
        logger.error(ex)
        return {
            "status": status,
            "status_code": status_code,
            "content": str(ex)
        }

