Funsize
============

[![Build Status](https://travis-ci.org/mozilla/build-funsize.svg?branch=master)](https://travis-ci.org/mozilla/build-funsize)

This service (Previously called [Senbonzakura](http://en.wikipedia.org/wiki/Byakuya_Kuchiki#Senbonzakura)) generates partial .MAR (Mozilla ARchive) files to update Firefox from Version A to Version B. It generates these on demand via API.


See [Wiki Page (Historical)](https://wiki.mozilla.org/User:Ffledgling/Senbonzakura) and [Wiki Page](https://wiki.mozilla.org/ReleaseEngineering/Funsize) for more details.

TODO
----

See TODO.md

Dev-Env Requirements
--------------------
- A Linux machine with docker installed
- Export the following variables to pass them to the funsize container: `FUNSIZE_AWS_ACCESS_KEY_ID`, `FUNSIZE_AWS_SECRET_ACCESS_KEY`, `FUNSIZE_S3_UPLOAD_BUCKET`
- run `./tests/launch_dev_env.sh` to generate 2 docker containers:
  - A container running RabbitMQ server. This container will be linked to the main container. See [docker documentation](http://docs.docker.com/userguide/dockerlinks/) for the details.
  - Funsize container will be running in foreground. The checkout root directory will be mounted to the `/app` directory inside the container. This means that your file changes will be propagated to the container.
- The application logs will show up in the `logs` directory


Running Unit Tests
------------------

Run `tox` command. It will create a temporary virtualenv under `.tox` and run the tests.


Client side
-----------

The client side to call for partials lies in this python package script:
- https://pypi.python.org/pypi/funsizer


License
-------

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

You can find a full copy of the MPL in the included LICENSE.md file.
