"""
funsize.backend.tasks
~~~~~~~~~~~~~~~~~~

This module contains a wrapper for the celery tasks that are to be run

"""

import time
from celery import Celery
from celery.utils.log import get_task_logger
import funsize.backend.core as core

app = Celery('tasks', broker='amqp://guest@localhost//')

logger = get_task_logger(__name__)


@app.task
def build_partial_mar(*args):
    """ Wrapper for actual method, to get timestamps and measurings
    """
    logger.info('STARTING TASK')
    start_time = time.time()
    core.build_partial_mar(*args)
    total_time = time.time() - start_time
    logger.info("Backup TOTAL TIME: %s", divmod(total_time, 60))
