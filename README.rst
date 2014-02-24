altair README
-------------

local (dev)
===========

mac
---

* Xcode + Command Line Tools をインストール
* homebrew をインストール

  * xz
  * redis

ubuntu
------

* apt でインストール

  * build-essential git libxml2-dev redis-server mysql-server xz s3cmd python-pip python-virtualenv python-dev libxslt1-dev


* MySQL をインストール

  * `MySQL Community Server 5.5.x / 5.6.x <http://dev.mysql.com/downloads/>`_
  * dmg からインストールするのが良いかも

* S3 からデータを取得して解凍

  * s3://ticketstar-dev-snapshots/yyyy-MM-DD/snapshot-*

* MySQL にユーザを作成して dump を import

  * import に時間がかかるので、事前にパラメータ調整しておくと早い

    * binlog や slowlog を出力しない設定にする
    * my.cnf で "skip_innodb_doublewrite" を設定
    * "innodb_flush_log_at_trx_commit = 0" にする

::

  mysql> CREATE DATABASE `altaircms` DEFAULT CHARSET utf8;
  mysql> CREATE DATABASE `ticketing` DEFAULT CHARSET utf8;
  mysql> GRANT ALL ON `altaircms`.* TO `altaircms`@'127.0.0.1' IDENTIFIED BY 'altaircms';
  mysql> GRANT ALL ON `ticketing`.* TO `ticketing`@'127.0.0.1' IDENTIFIED BY 'ticketing';

::

  $ xz -d snapshot-*.xz
  $ cat snapshot-altaircms*.sql | mysql -u altaircms -paltaircms altaircms
  $ cat snapshot-ticketing*.sql | mysql -u ticketing -pticketing ticketing


* 適当なディレクトリにソースを clone して buildout

::

  $ mkdir altair-devel
  $ cd altair-devel
  $ git clone git@github.com:ticketstar/altair
  $ git submodule init
  $ git submodule update
  $ easy_install virtualenv
  $ virtualenv --setuptools --no-site-packages env
  $ env/bin/pip install --upgrade setuptools
  $ cd altair/deploy/dev
  $ ../../../env/bin/python bootstrap.py -c ./buildout.local.cfg
  $ ./buildout.sh

* supervisor で起動

  * devproxy 以外は自動起動しないので、supervisorctl 経由で起動させる

::

  $ ./bin/supervisord

* devproxy 経由で動作確認

  * Firefox に `Proxy Selector <https://addons.mozilla.org/ja/firefox/addon/proxy-selector/>`_ をインストール
  * localhost:58080 経由で接続するように設定
  * stg2 のアドレスで確認

    * http://rt.stg2.rt.ticketstar.jp/
    * http://vissel.stg2.rt.ticketstar.jp/

Useful Resources
================

* `Pyramid Documentation <http://docs.pylonsproject.org/docs/pyramid.html>`_
* `Pyramid Migration Guide <http://bytebucket.org/sluggo/pyramid-docs/wiki/html/migration.html>`_


staging
=======

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
  $ ./buildout.sh


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
