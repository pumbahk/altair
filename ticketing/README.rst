altair.ticketing README
-----------------------

Setup
=====
::

  $ mkdir altair-devel
  $ cd altair-devel
  $ git clone git+ssh://git@github.com/ticketstar/altair
  $ cd altair
  $ git submodule init
  $ git submodule update
  $ easy_install virtualenv
  $ virtualenv env
  $ cd deploy/dev
  $ ../../env/bin/python bootstrap.py
  $ bin/buildout -c buildout.local.cfg


deploy/dev/bin/supervisorctl で利用したいインスタンスを起動する.


Generating seed data
====================

次のスクリプトでシードデータを生成::

  $ python src/ticketing/seed/gen.py > ticketing.sql

DB再生成::
  
  $ alembic -c alembic.ini upgrade head

シードデータのインポート::

  $ python initdb.py development.ini ticketing.sql

Set Up Database
=====================

データベースの作成::

 mysql>> CREATE DATABASE ticketing CHARACTER SET utf8;

alembic実行::

 $ alembic upgrade head

データ投入::

 $ python initdb.py development.ini ticketing.sql

Cart test how-to
================

次のコマンドでテスト環境用プロキシを立ち上げる::

  $ deploy/dev/bin/supervisorctl devproxy start

ブラウザのプロキシ設定を次の物に変更する::

  http://localhost:58080/

Useful Resources
================

* `Pyramid Documentation <http://docs.pylonsproject.org/docs/pyramid.html>`_
* `Pyramid Migration Guide <http://bytebucket.org/sluggo/pyramid-docs/wiki/html/migration.html>`_
