.. _object-topic:

トピックオブジェクト
-----------------------------

公演中止・変更情報、お知らせなど、時系列で一覧可能な情報を保持するオブジェクト。

.. code-block:: python

  {
      'topic': {
          "datetime": datetime, # 日付
          "title": unicode, # トピックタイトル
          "type": unicode, # トピックの種別（公演中止情報、お知らせ等）
          "content": unicode, # 本文
      }
  }

複数で利用する場合には次のようにリスト形式のオブジェクトを作る。
リストはあらかじめ日付でソートしておく想定。

.. code-block:: python

  {
      'topics' : [
          topic_object_1,
          topic_object_2,
          topic_object_3
      ]
  }

see also: :ref:`widget-topic`
