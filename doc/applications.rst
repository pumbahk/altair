.. -*- coding: utf-8 -*-

****************************************
アプリケーション構成
****************************************

各アプリケーションはpyramidを利用して記述されています。

altair.cms.admin

altair.cms.solr

altair.cms.usersite

altair.newsletter.admin

altair.ticketing.admin

altair.ticketing.booster.89ers

altair.ticketing.booster.bambitious

altair.ticketing.booster.bigbulls

altair.ticketing.cart

altair.ticketing.lot_worker

altair.ticketing.lots

altair.ticketing.orderreview

altair.ticketing.qrreader


devproxy

    開発用プロキシサーバーです。
    ローカルに開発用の疑似環境を構築する場合、
    本番環境と同じURLでアクセスできるようにするためのものです。
    このプロキシを通すと、本番環境へのURLはループバックアドレスに変換されます。



起動の仕組み
========================================   

各アプリケーションの起動には *supervisor* を使用しています。
*supervisor* はPythonで記述されたデーモン管理用フレームワークです。
詳しくはこちらをご覧ください。

http://supervisord.org/

*supervisor* の設定ファイルは以下です。
*buildout* でインストール時に *supervisorctl* 内に設定ファイルのパスが記述され配置されます。

$ALTAIR/deploy/dev/parts/supervisor/supervisord.conf

各デーモンは *pyramid* の *pserve* コマンドによって起動しています。
それぞれpyramid用の設定ファイルなどを引数に渡しています。

設定ファイルが格納されているディレクトリは以下です。

$ALTAIR/deploy/dev/conf


その他
========================================

起動に失敗したら・・・？
----------------------------------------

$ALTAIR/deploy/dev/parts/supervisor/supervisord.conf

には起動コマンドが記述されているので手動で起動してみてください。

環境がおかしいような場合にはbuildoutを再度実行するとなおる場合もあります。



