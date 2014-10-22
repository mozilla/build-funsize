set -e
echo "Starting celery as a daemon"
celery worker --detach -f /var/log/celerylog.log -l DEBUG -A funsize.backend.tasks

echo "Starting flask"
python funsize/frontend/api.py
