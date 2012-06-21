altair.ticketing README
-----------------------

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

Cart test how-to
================

次のコマンドでテスト環境用プロキシを立ち上げる::

  $ misc/proxy/run.sh start

ブラウザのプロキシ設定を次の物に変更する::

  http://localhost:58080/

テスト環境用プロキシを止めたい場合::

  $ misc/proxy/run.sh stop


Useful Resources
================

* `Pyramid Documentation <http://docs.pylonsproject.org/docs/pyramid.html>`_
* `Pyramid Migration Guide <http://bytebucket.org/sluggo/pyramid-docs/wiki/html/migration.html>`_
