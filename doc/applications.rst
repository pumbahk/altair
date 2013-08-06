.. -*- coding: utf-8 -*-

****************************************
アプリケーション構成
****************************************

各アプリケーションはpyramidを利用して記述されています。

altair.cms.admin

altair.cms.solr

altair.cms.usersite

altair.newsletter.admin

    メーリングリスト用のシステムです。
    ローカル環境へのアクセスは *0.0.0.0:8040* でアクセスできます。
    使用にはデータベースに *newsletter@localhost* というユーザが必要です。

altair.ticketing.admin

altair.ticketing.booster.89ers

altair.ticketing.booster.bambitious


    カート機能を提供します。
    
altair.ticketing.booster.bigbull

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



各種サイト
========================================

上記デーモンは様々なサイトのサービスを提供しています。
ローカル環境を作成したらどのURLにアクセスすればよいのでしょうか？
それらのデータはDBに対して次を発行することで確認できます。

::

    mysql> SELECT host_name, organization_id, Organization.short_name FROM Host JOIN Organization ON Host.organization_id=Organization.id WHERE host_name LIKE '%.stg2.rt.ticketstar.jp';

それぞれのデータは *backend* からアクセスできますが、
そのためには各サイト用のアカウントを使ってバックエンドにログインする必要があります。
各サイト用のアカウントは次のように確認できます。

::

    mysql> SELECT login_id, Organization.name, Organization.id FROM OperatorAuth JOIN Operator ON OperatorAuth.operator_id=Operator.id JOIN Organization;

*login_id* がログイン名になります。パスワードは *イツモノアレ* です。
わからない人は隣の席の人に聞いてみてください。
このアカウントでログインすると各サイトに関連したイベントを参照できるようになります。


その他
========================================

起動に失敗したら・・・？
----------------------------------------

$ALTAIR/deploy/dev/parts/supervisor/supervisord.conf

には起動コマンドが記述されているので手動で起動してみてください。

環境がおかしいような場合にはbuildoutを再度実行するとなおる場合もあります。



