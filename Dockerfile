FROM ubuntu:trusty
MAINTAINER "Anhad Jai Singh"

EXPOSE 5000

RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-dev supervisor python-pip gunicorn
# curl is used by the hook script
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y curl
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY / /app
RUN mkdir -p /perma/tools /app/logs /var/cache/funsize
RUN chmod 777 /app/logs
RUN chown daemon /var/cache/funsize

# TODO: publish the tools as a separate tarball?
ADD https://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/mar-tools/linux64/mar /perma/tools/
ADD https://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/mar-tools/linux64/mbsdiff /perma/tools/

ADD https://hg.mozilla.org/mozilla-central/raw-file/default/tools/update-packaging/make_incremental_update.sh /perma/tools/
ADD https://hg.mozilla.org/mozilla-central/raw-file/default/tools/update-packaging/unwrap_full_update.pl /perma/tools/
ADD https://hg.mozilla.org/mozilla-central/raw-file/default/tools/update-packaging/common.sh /perma/tools/

RUN chmod 755 /perma/tools/*

WORKDIR /app
RUN python setup.py develop

WORKDIR /
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["/usr/bin/supervisord"]
