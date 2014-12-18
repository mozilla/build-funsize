FROM ubuntu:trusty
MAINTAINER "Anhad Jai Singh"

EXPOSE 5000

RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-all python-dev supervisor celeryd
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN mkdir -p /perma/tools
COPY / /app

WORKDIR /app
RUN python setup.py develop
# run docker with --env=CELERY_BROKER=amqp://guest@localhost// --env=AWS_ACCESS_KEY_ID=1 --env=AWS_SECRET_ACCESS_KEY=1 --env=FUNSIZE_S3_UPLOAD_BUCKET=x --env=MBSDIFF_HOOK=x
CMD ["/usr/bin/supervisord"]
