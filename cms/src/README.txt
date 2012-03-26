=================
ALTAIR CMS
=================

::

 mkvirtualenv altairtest --no-site-packages
 cdvirtualenv
 git clone git@github.com:ticketstar/altair.git
 cd altair

 pip install .
 pip install -r pip-requirements.txt
 alembic current
 pmain  -c development.ini -s scripts.pmain.sqlstartup
 pserve development.ini --reload


ドキュメント
====================

Jenkinsでsphinxドキュメントをビルド

* https://dev.ticketstar.jp/cms/


ソースコード構成管理
==============================

git-flowを使って開発

* https://github.com/ticketstar/altair


イシュートラッキング
=================================

https://dev.ticketstar.jp/redmine-altair/projects/altair


テスト
===================

noseを利用
nosetestsでテスト::

 $ nosetests


CI
====================

Jenkinsを使用して、ポーリング、テスト、デプロイを実施。
dev.ticketstar.jpにあるが、socks経由じゃないとアクセスできない。

* http://10.160.41.149:8080/


ファイル共有
====================

Dropbox


開発サーバ
=======================

dev.ticketstar.jp

