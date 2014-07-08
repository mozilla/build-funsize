import senbonzakura.backend.core as core
from celery import Celery
import ConfigParser
import time
import logging

# All celery stuff goes in here
app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')

@app.task
def add(x, y):
    return x+y

@app.task
def build_partial_mar(*args):
    # Takes same args as core.build_partial_mar
    logging.info('STARTING TASK')
    start_time = time.time()
    core.build_partial_mar(*args)
    total_time = time.time() - start_time
    print "Backup TOTAL TIME: %s min %s sec" % divmod(total_time, 60)
    logging.info('Finished generating partial {2} in {0:.0f}m:{1:.3f}'.format(total_time/60, total_time%60, *args[5]))
