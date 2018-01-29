
import logging
import requests
import subprocess

def job(options):
    logger = logging.getLogger('xmr-stak-monitor')
    print ("ww")
    logger.warn("I'm working...")
    pag = get_web_page("{}/h".format(options["xmr_url"]))
    if pag["status"] != "OK":
        print("pag failed")
        logger.warn("pag failed.")
        print(pag)
        cmd = [ options["nssm_exe"], "restart", options["xmr_service"] ]
        oput = subprocess.check_output(cmd) #, shell=True)
        print(oput)
    else:
        print("pag ok.")
        logger.warn("pag ok.")

def get_web_page(url, http_method="GET"):
    """
    gets a web page
    :param url: string with the url to retrieve, for example: https://pepe.com:8000/sarasa
    :param http_method: string with the method to use ("GET" or "POST")
    :return: a dictionary with:
                    state: "ok" or "failure"

                    content: the web page html content in cas of success or the error in case of error.
    """
    status = "FAILURE"
    status_code = -1
    try:
        if (http_method.lower().strip() == 'get'):
            resp = requests.get(url)
        else:
            resp = requests.post(url)
        content = resp.content
        status_code = resp.status_code
        if status_code == 200:
            status = "OK"
        return {
            "status": status,
            "status_code": status_code,
            "content": content
            }
    except Exception as ex:
        return {
            "status": status,
            "status_code": status_code,
            "content": str(ex)
        }

