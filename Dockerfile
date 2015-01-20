FROM ubuntu:trusty
MAINTAINER "Anhad Jai Singh"

EXPOSE 5000

# Packages
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -q update && \
    apt-get install -y python-dev supervisor python-pip curl python-virtualenv

# copy the current directory as /app inside the image
COPY / /app
COPY configs/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /perma/tools /var/log/funsize /var/cache/funsize
RUN chmod 777 /var/log/funsize
RUN chown daemon /var/cache/funsize

# TODO: publish the tools as a separate tarball?
ADD https://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/mar-tools/linux64/mar /perma/tools/
ADD https://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/mar-tools/linux64/mbsdiff /perma/tools/

ADD https://hg.mozilla.org/mozilla-central/raw-file/default/tools/update-packaging/make_incremental_update.sh /perma/tools/
ADD https://hg.mozilla.org/mozilla-central/raw-file/default/tools/update-packaging/unwrap_full_update.pl /perma/tools/
ADD https://hg.mozilla.org/mozilla-central/raw-file/default/tools/update-packaging/common.sh /perma/tools/

RUN chmod 755 /perma/tools/*

WORKDIR /app
RUN virtualenv /venv
RUN /venv/bin/pip install gunicorn==19.1.1
RUN /venv/bin/python setup.py develop

WORKDIR /
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["/usr/bin/supervisord"]
