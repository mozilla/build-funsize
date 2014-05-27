from celery import Celery
import core

# All celery stuff goes in here

app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')

@app.task
def add(x, y):
    return x+y

@app.task
#def build_partial_mar(new_cmar_url, new_cmar_hash, old_cmar_url, old_cmar_hash):
def build_partial_mar(*args):
    # Takes same args as core.build_partial_mar
    core.build_partial_mar(*args)
