
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
    try:
        if (http_method.lower().strip() == 'get'):
            resp = requests.get(url)
        else:
            resp = requests.post(url)
        content = resp.content()
        if resp.status_code == 200:
            status = "OK"
        return {
            "status": status,
            "content": content
            }
    except Exception as ex:
        return {
            "status": status,
            "content": str(ex)
        }

