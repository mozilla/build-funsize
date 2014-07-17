set -e
echo "Starting RabbitMQ"
rabbitmq-server -detached
#echo AMQ pid: $!
echo "Starting celery as a daemon"
celery worker --detach -f /var/log/celerylog.log -l DEBUG -A senbonzakura.backend.tasks
#celery worker --detach -f /usr/local/var/log/celerylog.log -l DEBUG -A senbonzakura.backend.tasks
echo "Starting flask"
python senbonzakura/frontend/api.py
