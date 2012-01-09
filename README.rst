altair README
-------------

Setup
=====
::

  $ mkdir altair-devel
  $ cd altair-devel
  $ git clone git@github.com:ticketstar/altair
  $ easy_install virtualenv
  $ virtualenv env
  $ env/bin/easy_install pyramid
  $ cd vega
  $ ../env/bin/python setup.py develop
  $ ../env/bin/paster serve development.ini --reload

Useful Resources
================

* `Pyramid Documentation <http://docs.pylonsproject.org/docs/pyramid.html>`_
* `Pyramid Migration Guide <http://bytebucket.org/sluggo/pyramid-docs/wiki/html/migration.html>`_
