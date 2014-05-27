#from flask import Flask, request, Response
import celery
import flask
import time
import pprint

def make_celery(app):
    #celery_app = celery.Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery_app = celery.Celery(app.import_name)
    celery_app.conf.update(app.config)
    #celery_app.conf.update(
    #        CELERY_BROKER_URL='amqp://guest@localhost/',
    #        CELERY_RESULT_BACKEND='amqp',
    #    )
    TaskBase = celery_app.Task
    ##print "#"*30
    ##pprint.pprint(TaskBase.request_stack)
    ##print "#"*30
    class ContextTask(TaskBase):
        abstract=True # What is this for exactly?
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery_app.Task = ContextTask
    ##print "#"*30
    ##pprint.pprint(ContextTask.request_stack)
    ##print "#"*30
    return celery_app

app = flask.Flask(__name__)
app.config.update(
        CELERY_BROKER_URL='amqp://guest@localhost/',
        CELERY_RESULT_BACKEND='amqp'
        )

celery_app = make_celery(app)

@celery_app.task()
def long():
    print "Sleeping"
    time.sleep(2)
    print "Done sleeping"
    return "Finito"
