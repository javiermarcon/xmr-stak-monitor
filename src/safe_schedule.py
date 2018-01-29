"""
This file is a copy of mplewis's code,
taken from https://gist.github.com/8483f1c24f2d6259aef6.git
"""

import logging
from traceback import format_exc
import datetime

from schedule import Scheduler


logger = logging.getLogger('xmr-stak-monitor')


class SafeScheduler(Scheduler):
    """
    An implementation of Scheduler that catches jobs that fail, logs their
    exception tracebacks as errors, optionally reschedules the jobs for their
    next run time, and keeps going.
    Use this to run jobs that may or may not crash without worrying about
    whether other jobs will run or if they'll crash the entire script.
    """

    def __init__(self, reschedule_on_failure=True):
        """
        If reschedule_on_failure is True, jobs will be rescheduled for their
        next run as if they had completed successfully. If False, they'll run
        on the next run_pending() tick.
        """
        self.reschedule_on_failure = reschedule_on_failure
        # # este super es pra python 3
        #super().__init__()
        # # para python 2 usar el super asi
        Scheduler.__init__(self)

    def _run_job(self, job):
        try:
            # # este super es pra python 3
            #super()._run_job(job)
            # # para python 2 usar el run asi
            Scheduler._run_job(self, job)

        except Exception:
            logger.error(format_exc())
            job.last_run = datetime.datetime.now()
            job._schedule_next_run()