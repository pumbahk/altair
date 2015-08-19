.. -*- coding: utf-8 -*-

**************************************************
alshain - Altair Debugging Utility
**************************************************


alshainはaltair用のデバッグ用utilityです。

INSTALL
======================

alshainはaltairのリポジトリに自動しました。

::

   $ ls
   alshain  # <- ココにalshainのソースツリーがあるとして
   $ pip install ./alshain


SETUP
-----------------------

alshainをinstallするとalshainコマンドが使用できます。
alshainコマンドを使用する場合は次の環境変数を設定する必要があります。

ALTAIR
    altairのソースツリーのrootの絶対パスです。
    指定しない場合は */srv/altair/current* が使われます。


ALTAIR_DEPLOY
    altairを動かす環境です。(dev, staging, qa, production　のいずれかです。)
    指定しない場合は *dev* が使われます。

ALTAIR_SUDO
    altairの操作でsudoを使用する場合のユーザ名です。
    例えば *buildout.sh* を実行する場合はsudo付きで実行されます。
    指定しない場合は sudo実行しません。


ex) local環境での設定::

    $ export ALTAIR=/my/work/altair/directory
    $ export ALTAIR_DEPLOY=dev
    $ export ALTAIR_SUDO

ex) stg2環境での設定::

    $ export ALTAIR=/srv/altair/current
    $ export ALTAIR_DEPLOY=staging
    $ export ALTAIR_SUDO=ticketstar



HOW TO USE IT
=======================

dev-snapshotをいれる::

     $ alshain db restore

デバッガを使う(altair.ticketing.admin.defaultの場合)::

    $ alshain debug altair.ticketing.admin.default

mysql, postfix, redis, rabbitmqの起動::

     $ alshain middleware start

supervisordの起動::

    $ alshain daemon start

supervisordの停止::

    $ alshain daemon stop

supervisorctl restart allする::

    $ alshain ctl restart all

alembicでticketingをupgrade headする::

     $ alshain alembic ticketing upgrade head

alembicでcmsをdowngrade -5する::

     $ alshain alembic cms downgrade -5

テストを実行する::

     $ alshain verify ticketing
     $ alshain verify cms
     $ alshain verify altairlib

バッチの実行(augus_uploadを実行)::

     $ alshain batch augus_upload

git の操作(git statusをする)::

     $ alshain git status

pshellの起動::

     $ alshain pshell

backendtest(管理画面のE2Eテスト)を実行する::

     $ alshain backendtest

altairpyを使う::

     $ alshain py

コマンド一覧を確認する::

     $ alshain  --command-list

使い方を確認する::

     $ alshain help

等。
