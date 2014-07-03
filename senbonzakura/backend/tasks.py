from celery import Celery
import senbonzakura.backend.core as core
import ConfigParser

# All celery stuff goes in here
app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')

@app.task
def add(x, y):
    return x+y

@app.task
def build_partial_mar(*args):
    # Takes same args as core.build_partial_mar
    core.build_partial_mar(*args)
