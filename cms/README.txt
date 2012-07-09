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


stagingからの以降
-----------------------

:: 

	ALTER TABLE site DROP FOREIGN KEY fk_site_client_id_to_client_id;
	ALTER TABLE event DROP FOREIGN KEY fk_event_client_id_to_client_id;
	ALTER TABLE performance DROP FOREIGN KEY fk_performance_client_id_to_client_id;
	ALTER TABLE user DROP FOREIGN KEY fk_user_site_id_to_site_id;
	ALTER TABLE operator DROP FOREIGN KEY fk_operator_client_id_to_client_id;
	ALTER TABLE apikey DROP FOREIGN KEY fk_apikey_client_id_to_client_id;
	ALTER TABLE category DROP FOREIGN KEY fk_category_site_id_to_site_id;
	ALTER TABLE hotword DROP FOREIGN KEY fk_hotword_site_id_to_site_id;
	ALTER TABLE layout DROP FOREIGN KEY fk_layout_site_id_to_site_id;
	ALTER TABLE layout DROP FOREIGN KEY fk_layout_client_id_to_client_id;
	ALTER TABLE page DROP FOREIGN KEY fk_page_site_id_to_site_id;
	ALTER TABLE promotion DROP FOREIGN KEY fk_promotion_site_id_to_site_id;
	ALTER TABLE topcontent DROP FOREIGN KEY fk_topcontent_site_id_to_site_id;
	ALTER TABLE topcontent DROP FOREIGN KEY fk_topcontent_client_id_to_client_id;
	ALTER TABLE topic DROP FOREIGN KEY fk_topic_site_id_to_site_id;
	ALTER TABLE topic DROP FOREIGN KEY fk_topic_client_id_to_client_id;
	ALTER TABLE widget DROP FOREIGN KEY fk_widget_site_id_to_site_id;
	ALTER TABLE widgetdisposition DROP FOREIGN KEY fk_widgetdisposition_site_id_to_site_id;
	ALTER TABLE asset DROP FOREIGN KEY asset_ibfk_1;

	DROP TABLE page_accesskeys;
	DROP TABLE organization;

	## ここでalembicを実行

    alter table page add column published tinyint(1);
    update page set published = 1;
    update asset set organization_id = 1;
    update assettag set organization_id = 1;
    update category set organization_id = 1;
    update event set organization_id = 1;
    update flash_asset set organization_id = 1;
    update hotword set organization_id = 1;
    update image_asset set organization_id = 1;
    update layout set organization_id = 1;
    update movie_asset set organization_id = 1;
    update operator set organization_id = 1;
    update page set organization_id = 1;
    update page_accesskeys set organization_id = 1;
    update pagesets set organization_id = 1;
    update pagetag set organization_id = 1;
    update topcontent set organization_id = 1;
    update topic set organization_id = 1;
    update promotion set organization_id = 1;
    update promotion_unit set organization_id = 1;
    update widgetdisposition set organization_id = 1;
