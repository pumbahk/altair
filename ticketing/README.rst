vega README
-----------

Setup
=====
::

  $ mkdir altair-devel
  $ cd altair-devel
  $ git clone git+ssh://git@github.com/ticketstar/altair
  $ easy_install virtualenv
  $ virtualenv env
  $ env/bin/easy_install pyramid
  $ source env/bin/activate
  $ cd altair/ticketing/src
  $ python setup.py develop
  $ python seed_import.py
  $ ../../../env/bin/paster serve development.ini --reload

Useful Resources
================

* `Pyramid Documentation <http://docs.pylonsproject.org/docs/pyramid.html>`_
* `Pyramid Migration Guide <http://bytebucket.org/sluggo/pyramid-docs/wiki/html/migration.html>`_
