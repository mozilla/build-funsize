FROM ubuntu:trusty
EXPOSE 56725
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -yqq rabbitmq-server
COPY rabbitmq.config /etc/rabbitmq/rabbitmq.config
USER rabbitmq

CMD ["/usr/sbin/rabbitmq-server"]
