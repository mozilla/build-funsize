Senbonzakura
============

[![Build Status](https://travis-ci.org/ffledgling/Senbonzakura.svg?branch=master)](https://travis-ci.org/ffledgling/Senbonzakura)

This service (Previously called [Senbonzakura](http://en.wikipedia.org/wiki/Byakuya_Kuchiki#Senbonzakura)
for now) will generate partial .MAR (Mozilla ARchive) files for updates from
Version A to Version B on demand.


See [Wiki Page](https://wiki.mozilla.org/User:Ffledgling/Senbonzakura) for more details.

TODO
----

See TODO.md

Dev-Env Requirements
--------------------

- Setup a virtualenv
- Clone source
- Run `python setup.py develop` inside your virtualenv
- You're good to go!

Use infrastructure with Docker via Vagrant
------------------------------------------

To deploy & test the infrastructure on a particular machine, the Docker platform can easily be used.
Docker Engine uses Linux-specific kernel features, so to run it within OS X/Windows a lightweight virtual machine is needed.

If you want to use Docker with Vagrant you need to:

   1. Download Vagrant from here http://www.vagrantup.com/downloads.html
   2. Go into your working directory
   3. Find the `Vagrantfile` sample from this repo placed under `Docker` folder.
   4. Rename `Vagrantfile.sample` to `Vagrantfile`.
   5. From `Docker` directory run:
       * ` $vagrant up funsizeapp --provider=docker`


A fully functional Vagrant container with Docker provisioning automatically installed software has been created.

License
-------

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

You can find a full copy of the MPL in the included LICENSE.md file.
