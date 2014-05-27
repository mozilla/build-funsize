Senbonzakura
============

This service (I'm calling it [Senbonzakura](http://en.wikipedia.org/wiki/Byakuya_Kuchiki#Senbonzakura)
for now) will generate partial .mar (Mozilla ARchive) files for updates from 
Version A to Version B on demand.


See [Wiki Page](https://wiki.mozilla.org/User:Ffledgling/Senbonzakura) for more details.

TODO
----

**Overall TODOs:**
- Write unit-tests for all the functions.
- Figure out how to set them up to run with `python setup.py test`
- How to do the packaging

**Open Issues:**

- Integrate with flask
- Figure out the tooling issues
- Talk about and flesh out the caching
- Flesh out the dev-env requirements
- Get feedback

Dev-Env Requirements
--------------------

- Setup a virtualenv
- Clone source
- You're good to go!

These will/might be needed in the future, but aren't used by current code

1. Flask
2. requests
3. Nose
