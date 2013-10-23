.. contents::

設定
===============

altair.mq.url
--------------------------

rabbitmqへの接続URL

例::

  altair.mq.url = amqp://guest:guest@localhost:5672/%2F

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

mserveはtronadoによるIOLoopでキューを監視します。
そのため、mserveプロセスはシングルスレッドで動作しています。

Task
=============

Consumerが受け取ったメッセージはTaskに渡されます。
Taskの追加は ``task_config`` で行います。

::
    @task_config(root_factory=WorkerResource, queue="lots")
    def elect_lots_task(context, message):
        ....


``root_factory`` は、 ``message`` を受け取るcallableです。

messageは、paramプロパティを持っています。
publisherが作成したデータがjsonフォーマットの場合、paramプロパティからjson.loadされた値を利用可能です。


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
