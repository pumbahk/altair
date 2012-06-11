=================
ALTAIR CMS
=================

deploy方法
::

   mkvirtualenv altairtest --no-site-packages
   cdvirtualenv
   git clone git@github.com:ticketstar/altair.git
   cd altair

   cd cms
   python setup.py dev
   python setup.py upgrade_db

   ## 
   ## mysqlでdatabase作成altaircms
   ##

   ## デモデータの投入
   pmain -c development.ini -s altaircms.scripts.pmain.insert_demodata

   ## 
   ## solrを利用したい場合はinstall solrの項参照
   ##

   ## cmsのアプリを立ち上げる
   pserve development.ini --reload # port:6543
   ## usersiteのアプリを立ち上げる
   pserve usersite.development.ini --reload # port:5432



csvからevent,performanceのデータを取り込む
-------------------------------------------
イベントなど作る(400件くらい)::

	$ pwd # altaircms/cms
	$ cd csvs
	$ make run



install solr
----------------------------------------

javaが必要::

   sudo apt-get install openjdk-6-jdk #ubuntu

solrの環境作成にはbuildoutを使っている。

buildout::

   pwd # ./altair/cms
   python setup.py dev_solr
   cd ../deploy
   buildout init
   ./bin/buildout -N -v install

development.ini,usersite.development.ini::

   ## solr
   altaircms.solr.server.url = http://localhost:8080/solr
   altaircms.solr.search.utility = altaircms.solr.api.SolrSearch
   # altaircms.solr.search.utility = altaircms.solr.api.DummySearch

solrのインスタンスを立ち上げる::

   ./depoly/bin/solr-instance start
  


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
 $ python setup.py coverage


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

