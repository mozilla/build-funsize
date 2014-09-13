set -e
echo "Starting RabbitMQ"
rabbitmq-server -detached

echo "Starting celery as a daemon"
celery worker --detach -f /var/log/celerylog.log -l DEBUG -A senbonzakura.backend.tasks

echo "Starting flask"
python senbonzakura/frontend/api.py
