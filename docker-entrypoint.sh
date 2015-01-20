#!/bin/sh

mkdir -p /var/log/supervisor /var/log/funsize
chmod 777 /var/log/funsize
exec "$@"
