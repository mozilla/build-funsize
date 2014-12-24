"""
Celery configuration for dev environment
export FUNSIZE_CELERY_CONFIG="funsize.backend.config.dev" to use it
"""
import os

CELERY_ACKS_LATE = True
CELERY_DEFAULT_QUEUE = "funsize_dev"
BROKER_URL = os.environ.get('BROKER_URL')
