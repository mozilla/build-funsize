#!/bin/bash

if [ "$TRAVIS_PULL_REQUEST" != "false" -a "$FUNSIZE_CACHE_TYPE" = "s3" ]; then
    echo "S3 integration test doesn't work on pull requests. Skipping..."
    exit 0
fi

set -x
set -e

script_dir=$(dirname $0)

CELERY_PID=
FLASK_PID=
export BROKER_URL="amqp://guest@localhost//"
export FUNSIZE_CELERY_CONFIG="funsize.backend.config.dev"
export MBSDIFF_HOOK="$script_dir/../funsize/backend/mbsdiff_hook.sh \
    -A http://127.0.0.1:5000/cache -c /tmp/funsize-patches"
export TOOLS_DIR=/tmp/tools

mkdir -p $TOOLS_DIR
wget -O $TOOLS_DIR/mar https://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/mar-tools/linux64/mar
wget -O $TOOLS_DIR/mbsdiff https://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/mar-tools/linux64/mbsdiff

wget -O $TOOLS_DIR/make_incremental_update.sh https://hg.mozilla.org/mozilla-central/raw-file/b052018cf239/tools/update-packaging/make_incremental_update.sh
wget -O $TOOLS_DIR/unwrap_full_update.pl https://hg.mozilla.org/mozilla-central/raw-file/b052018cf239/tools/update-packaging/unwrap_full_update.pl
wget -O $TOOLS_DIR/common.sh https://hg.mozilla.org/mozilla-central/raw-file/b052018cf239/tools/update-packaging/common.sh

chmod 755 $TOOLS_DIR/*

celery worker -f /tmp/celery.log --purge --detach --pidfile=/tmp/celery.pid \
    -l DEBUG -A funsize.backend.tasks --config=$FUNSIZE_CELERY_CONFIG

gunicorn -w 4 -b :5000 --daemon --pid=/tmp/flask.pid \
    --access-logfile=/tmp/flask.log funsize.frontend.api:app

on_exit(){
    kill `cat /tmp/celery.pid` || :
    kill `cat /tmp/flask.pid` || :
    cat /tmp/celery.log
    cat /tmp/flask.log
}

trap on_exit EXIT

sleep 5
ps --pid `cat /tmp/celery.pid`
ps --pid `cat /tmp/flask.pid`

python $script_dir/integration_test.py -j2 -n4
