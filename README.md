Senbonzakura
============

[![Build Status](https://travis-ci.org/ffledgling/Senbonzakura.svg?branch=master)](https://travis-ci.org/ffledgling/Senbonzakura)

This service (I'm calling it [Senbonzakura](http://en.wikipedia.org/wiki/Byakuya_Kuchiki#Senbonzakura)
for now) will generate partial .mar (Mozilla ARchive) files for updates from 
Version A to Version B on demand.


See [Wiki Page](https://wiki.mozilla.org/User:Ffledgling/Senbonzakura) for more details.

TODO
----

**Overall TODOs:**
- Write unit-tests for all the functions.
- Figure out the tooling issues
- Talk about and flesh out the caching
- Figure out how to set them up to run with `python setup.py test`
- How to do the packaging
- Flesh out the dev-env requirements
- Get feedback

**Open Issues:**

- ~~Integrate with flask~~
- Possibly dump fetching and similar tasks to a celery worker each.

Dev-Env Requirements
--------------------

- Setup a virtualenv
- Clone source

- Install the latest versions of:

  1. Celery
  2. Flask
  3. RabbitMQ
  4. Requests
  5. SQLAlchemy

- You're good to go!

The following will/might be needed in the future, but aren't used by current code:

1. Nose
2. Requests
