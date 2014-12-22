#!/bin/bash

set -e
set -x
script_dir=$(dirname $0)

cd $script_dir/..
docker build -t funsize .
docker build -t rabbitmq tests/rabbitmq
docker rm -f funsize || :
docker rm -f rabbitmq || :
docker run -d  -P -p 56725:56725 -p 5555:5555 --name rabbitmq rabbitmq

sleep 2
docker run -v $(pwd):/app \
    --link rabbitmq:rabbitmq \
    -p 5000:5000 -P --rm \
    --env=CELERY_BROKER=amqp://guest@rabbitmq// \
    --env=AWS_ACCESS_KEY_ID=$FUNSIZE_AWS_ACCESS_KEY_ID \
    --env=AWS_SECRET_ACCESS_KEY=$FUNSIZE_AWS_SECRET_ACCESS_KEY \
    --env=FUNSIZE_S3_UPLOAD_BUCKET=$FUNSIZE_S3_UPLOAD_BUCKET \
    --env=MBSDIFF_HOOK="/app/funsize/backend/mbsdiff_hook.sh -A http://127.0.0.1:5000/cache -c /var/cache/funsize" \
    --env=FUNSIZE_DEBUG=1 \
    -i -t --name funsize funsize $@

trap "docker stop rabbitmq" EXIT
