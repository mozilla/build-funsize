set -e
echo "Starting RabbitMQ"
rabbitmq-server &
echo AMQ pid: $!
echo "Starting celery as a daemon"
celery worker --detach -f /usr/local/var/log/celeryworker.log -l DEBUG -A senbonzakura.backend.tasks
echo "Starting flask"
python senbonzakura/frontend/api.py
