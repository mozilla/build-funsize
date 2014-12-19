FROM ubuntu:trusty
MAINTAINER "Anhad Jai Singh"

EXPOSE 5000

RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-dev supervisor python-pip
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY / /app
RUN mkdir -p /perma/tools /app/logs
RUN chmod 777 /app/logs

WORKDIR /app
RUN python setup.py develop

WORKDIR /
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["/usr/bin/supervisord"]
