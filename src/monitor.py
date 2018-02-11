import datetime
import eventlet
import json
import os
import requests
import subprocess

def make_paths_and_urls(options):
    nspath = os.path.abspath(options["common"]["nssm_exe"]).replace('\\', '\\\\')
    urls = {}
    for service in options["services"]:
        if not "type" in service:
            service["type"] = "xmrig"
        check_content = True
        if str(service["type"]).lower().strip() != "xmrig":
            check_content = False
            service["xmr_url"] = "{}/h".format(service["xmr_url"])
        urls[service["xmr_service"]] = (service["xmr_url"], check_content)
    return (nspath, urls)

def do_restart(nspath, svc, logger):
    cmd = [nspath, "restart", svc]
    logger.debug("primer call: {}".format(" ".join(cmd)))
    try:
        logger.debug("inicio_exe")
        subprocess.run(cmd, check=False)
        # Para python2 usar subprocess.call(cmd)
        logger.debug("fin exe")
    except Exception as ee:
        logger.debug(ee)

def job(urls, nspath, page_timeout, logger):
    logger.debug("I'm working...")
    for svc in urls:
        (url, check_content) = urls[svc]
        pag = get_web_page(url, logger, page_timeout)
        logger.debug("got page {} for {}".format(url, svc))
        http_content_ok = check_http_content(pag["content"], check_content)
        if pag["status"] != "OK" or not http_content_ok:
            logger.warn("page failed at {}.".format(datetime.datetime.now()))
            logger.debug(pag)
            do_restart(nspath, svc, logger)
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
        with eventlet.Timeout(timeout):
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

def check_http_content(response, do_check):
    if not do_check:
        print(response, do_check)
        return True
    jresp = json.loads(response)
    for thread in jresp["hashrate"]["threads"]:
        if thread[0] == 0.0:
            return False
    return True
