FROM ubuntu:utopic
EXPOSE 56725
EXPOSE 5555
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -yqq rabbitmq-server python-flower supervisor
COPY rabbitmq.config /etc/rabbitmq/rabbitmq.config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
