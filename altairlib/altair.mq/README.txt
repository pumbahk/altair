.. contents::

Publisher
===========

Publisherはpublishメソッドで、キューにデータを追加します。
例::

    publisher.publish(body=json.dumps(body),
                      routing_key="lots",
                      properties=dict(content_type="application/json"))

publishメソッドでは、bodyパラメータでデータ、routing_keyでキューの名前を指定します。


Consumer
============

ワーカーは mserveコマンドでキューを監視します。
mserveコマンドは、コマンドライン引数で指定されたconfigファイルの設定を利用します。

mserveはtornadoによるIOLoopでキューを監視します。
そのため、mserveプロセスはシングルスレッドで動作しています。

Task
=============

Consumerが受け取ったメッセージはTaskに渡されます。
Taskの追加は ``task_config`` で行います。

::
    @task_config(root_factory=WorkerResource, queue="lots")
    def elect_lots_task(context, request):
        ....


``root_factory`` は、 ``request`` を受け取るcallableです。

requestは普通のRequestオブジェクトです。
paramプロパティにpublisherから渡されたパラメータが入ります。


Publisher / Consumer の追加方法
===================================

``Configurator`` の ``add_publisher_consumer`` ディレクティブでタスクと設定項目の関連づけを定義する

例::

    # cart タスクの設定項目を altair.ticketing.cart.mq.XXXX とする
    config.add_publisher_consumer('cart', 'altair.ticketing.cart.mq')


設定項目
------------

PREFIX
--------------------------

consumer と publisher の Factory を指定する

例::

    PREFIX = altair.mq.consumer.pika_client_factory
             altair.mq.publisher.pika_publisher_factory


もし Pika を使わずに同期的にタスクを実行したい場合は::

    XXX = altair.mq.publisher.locally_dispatching_publisher_consumer_factory
    XXX.routes = {ルーティングキーのパターン}:{キュー名}

のようにする。

PREFIX.url
--------------------------

rabbitmqへの接続URL。

Publisher / consumer が

* ``altair.mq.consumer.pika_client_factory``
* ``altair.mq.publisher.pika_publisher_factory``

のときに利用可能。

例::

  PREFIX.url = amqp://guest:guest@localhost:5672/%2F


XXX.routes
-------------

ルーティングキーとキュー名の対応付け (複数指定可) を行う。
Publisher / consumer が ``altair.mq.publisher.locally_dispatching_publisher_consumer_factory`` の場合のみ利用可能。


ルーティングキーのパターンにはワイルドカードが使える。

例::

    XXX.routes = route
                 r.*


タスクの追加方法
============================

あらかじめ決めておくこと
----------------------------

- キューの名前
- Messageに含めるデータ（json形式にすると、タスク側で引き出しやすい）

Publisherの処理
-------------------------

# Publisherクラスを直接使うか、 ``getUtlity(IPublisher)`` などでregistryから取り出す
# 決めたキューの名前をrouting_keyとして上記データをbodyに渡すpublish処理を書く

タスク
---------------

# Messageを受け取るroot_factoryの処理(多分クラス)を書く
# タスク処理の関数を同じキューの名前で task_configで登録する
# task_configがconfig.scanされる範囲に含まれていることを確認する


各種確認方法
---------------------

キューの中の要素数を見る::

    $ sudo rabbitmqctl list_queues

キューを削除する::

    $ amqp-delete-queue --queue=lots

キューにデータを投げる::

    $ amqp-publish --routing-key=lots --body='{"name": "...."}' --content-type='application/json'
