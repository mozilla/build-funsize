"""
funsize.backend.tasks
~~~~~~~~~~~~~~~~~~

This module contains a wrapper for the celery tasks that are to be run

"""

import time
from celery import Celery
from celery.utils.log import get_task_logger
import funsize.backend.core as core
import funsize.utils.oddity as oddity

app = Celery('tasks', broker='amqp://guest@localhost//')
celery_config = {
    'CELERY_ACKS_LATE': True,
}
app.conf.update(celery_config)
logger = get_task_logger(__name__)


@app.task
def build_partial_mar(*args):
    """ Wrapper for actual method, to get timestamps and measurings """
    logger.info('STARTING TASK')
    start_time = time.time()

    try:
        core.build_partial_mar(*args)
    except (oddity.ToolError, oddity.CacheError) as exc:
        # TODO: maybe a unittool clobber here? or cache clean for entry?
        logger.info("Going to retry the job.")
        raise build_partial_mar.retry(countdown=60, exc=exc, max_retries=2)

    total_time = time.time() - start_time
    logger.info("Backup TOTAL TIME: %s", divmod(total_time, 60))
