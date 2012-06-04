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


ステージングたちあげ
================================

buildout環境の確認
::

  $ cd /srv/altair/deploy
  $ ls bin/buildout

buildoutがあれば環境あり。
ない場合は、以下の``buildout環境構築`` を行う


buildout環境構築

::

  $ cd /srv/altair/deploy
  $ python bootstrap.py -d
  $ bin/buildout


現在実行しているサービスの確認
=========================================================

::

  $ cd /srv/altair/deploy
  $ bin/supervisordctl
  supervider> status

ソースアップグレードしてからのリスタート
=========================================================

DB環境などの更新はそれぞれで行うこと

::

  $ cd /srv/altair/deploy
  $ bin/supervisordctl
  supervisor> restart all
