set -e
rabbitmq-server &
celery worker --detach -f /usr/local/var/log/celeryworker.log -l DEBUG -A senbonzakura.backend.tasks
python senbonzakura/frontend/api.py
