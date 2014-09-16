"""
funsize.backend.tasks
~~~~~~~~~~~~~~~~~~

This module contains a wrapper for the celery tasks that are to be run

"""

import time
import logging
from celery import Celery

import funsize.backend.core as core

app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')


@app.task
def build_partial_mar(*args):
    """ Wrapper for actual method, to get timestamps and measurings
    """
    logging.info('STARTING TASK')
    start_time = time.time()
    core.build_partial_mar(*args)
    total_time = time.time() - start_time
    logging.info("Backup TOTAL TIME: %s", divmod(total_time, 60))
