"""
funsize.backend.tasks
~~~~~~~~~~~~~~~~~~

This module contains a wrapper for the celery tasks that are to be run

"""

import time
from celery import Celery
from celery.utils.log import get_task_logger
import funsize.backend.core as core

app = Celery(__name__)
app.config_from_envvar("FUNSIZE_CELERY_CONFIG")
logger = get_task_logger(__name__)


@app.task
def build_partial_mar(*args, **kwargs):
    """ Wrapper for actual method, to get timestamps and measurings """
    start_time = time.time()
    try:
        core.build_partial_mar(*args, **kwargs)
    except Exception as exc:
        logger.info("Retrying the failed task")
        raise build_partial_mar.retry(countdown=30, exc=exc, max_retries=4)

    total_time = time.time() - start_time
    logger.info("TOTAL TIME: %s", divmod(total_time, 60))
