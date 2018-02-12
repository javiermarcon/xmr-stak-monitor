import datetime
import eventlet
import json
import os
import requests
import subprocess
import threading
import traceback
#import shlex

class Command(object):
    """
    code from: https://gist.github.com/kirpit/1306188
    Enables to run subprocess commands in a different thread with TIMEOUT option.
    Based on jcollado's solution:
    http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933
    """
    command = None
    process = None
    status = None
    output, error = '', ''

    def __init__(self, command, logger):
        #if isinstance(command, basestring):
        #    command = shlex.split(command)
        self.command = command
        self.logger = logger
        self.logger.debug("init de Command")

    def run(self, timeout=None, **kwargs):
        """ Run a command then return: (status, output, error). """
        self.logger.debug("Inicio run en command")
        def target(**kwargs):
            try:
                self.logger.debug("inicio process en command")
                self.process = subprocess.Popen(self.command, **kwargs)
                self.logger.debug("---1---")
                self.output, self.error = self.process.communicate()
                self.logger.debug("---2---")
                self.status = self.process.returncode
                self.logger.debug("fin process en command")
            except:
                self.logger.debug("error en Command")
                self.error = traceback.format_exc()
                self.status = -1
        # default stdout and stderr
        if 'stdout' not in kwargs:
            self.logger.debug("---stdout---")
            kwargs['stdout'] = subprocess.PIPE
        if 'stderr' not in kwargs:
            self.logger.debug("---stderr---")
            kwargs['stderr'] = subprocess.PIPE
        # thread
        self.logger.debug("---instancio thread---")
        thread = threading.Thread(target=target, kwargs=kwargs)
        self.logger.debug("---inicio thread---")
        thread.start()
        self.logger.debug("---join thread---")
        thread.join(timeout)
        if thread.is_alive():
            self.logger.debug("---alive thread, terminate---")
            self.process.terminate()
            self.logger.debug("---join 1 thread---")
            thread.join()
        self.logger.debug("---return command---")
        return self.status, self.output, self.error

class Monitor():

    def __init__(self, options, logger):
        self.logger = logger
        self.options = options
        self.timeout = int(options["common"]["page_timeout"])
        self.nspath = os.path.abspath(options["common"]["nssm_exe"]).replace('\\', '\\\\')
        self.jobs = self.make_jobs_dict()

    def make_jobs_dict(self):
        jobs = {}
        for service in self.options["services"]:
            if not "type" in service:
                service["type"] = "xmrig"
            check_content = True
            if str(service["type"]).lower().strip() != "xmrig":
                check_content = False
                service["xmr_url"] = "{}/h".format(service["xmr_url"])
            params = {}
            params["url"] = service["xmr_url"]
            params["check_content"] = check_content
            for action in ["restart", "status"]:
                cmd = [self.nspath, action, service["xmr_service"]]
                params["cmd_{}".format(action)] = Command(cmd, self.logger)
            jobs[service["xmr_service"]] = params
        return jobs

    def do_restart(self, svc):
        self.logger.debug("primer call: {}".format(svc))
        try:
            self.logger.debug("inicio_exe")
            (a, b, c) = self.jobs[svc]["cmd_restart"].run(timeout=self.timeout)
            self.logger.debug(a)
            self.logger.debug(b)
            self.logger.debug(c)
            #os.system(joined_cmd)
            #subprocess.run(cmd, check=False)
            # Para python2 usar subprocess.call(cmd)
            self.logger.debug("fin exe")
        except Exception as ee:
            self.logger.debug(ee)

    def run(self):
        self.logger.debug("I'm working...")
        for svc in self.jobs:
            url = self.jobs[svc]["url"]
            pag = self.get_web_page(url)
            self.logger.debug("got page {} for {}".format(url, svc))
            if not self.check_http_response(pag, self.jobs[svc]["check_content"]):
                self.logger.warn("page failed at {}.".format(datetime.datetime.now()))
                self.logger.debug(pag)
                self.do_restart(svc)
                self.logger.debug("restarted..")
            else:
                self.logger.debug("pag ok.")

    def get_web_page(self, url, http_method="GET"):
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
        self.logger.debug("Inicio Request ({})a {}".format(http_method, url))
        try:
            eventlet.monkey_patch()
            with eventlet.Timeout(self.timeout):
                if (http_method.lower().strip() == 'get'):
                    resp = requests.get(url, verify=False)
                    self.logger.debug("Fin request Get")
                else:
                    resp = requests.post(url, verify=False)
                    self.logger.debug("Fin Request POST")
                content = resp.content
                status_code = resp.status_code
                if status_code == 200:
                    status = "OK"
                self.logger.debug("status:{} resp_code{}".format(status, status_code))
                return {
                    "status": status,
                    "status_code": status_code,
                    "content": content
                    }
        except (Exception, eventlet.timeout.Timeout) as ex:
            self.logger.error("error trayendo web page")
            self.logger.error(ex)
            return {
                "status": status,
                "status_code": status_code,
                "content": str(ex)
            }

    def check_http_response(self, response, do_check):
        if response["status"] != "OK":
            self.logger.debug("http response failed. Not OK.")
            return False
        if not do_check:
            self.logger.debug("http response ok, no content check..")
            return True
        try:
            jresp = json.loads(response["content"])
            for thread in jresp["hashrate"]["threads"]:
                if thread[0] == 0.0:
                    self.logger.debug("http response failed, thread on 0.0")
                    return False
            self.logger.debug("http response ok with content checked.")
            return True
        except ValueError as er:
            self.logger.debug("Error checking http response: {}".format(er))
            return False
