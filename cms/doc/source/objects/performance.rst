.. _object-performance:

公演オブジェクト
-----------------------------------

イベント内の公演を表すオブジェクト。

.. code-block:: python

 {
     'performance': {
         'event_id': int, # event ID
         'title': unicode, # 公演名
         'performance_open': datetime, # 公演開始日時
         'performance_close': datetime, # 公演終了日時
     }
 }

see also: :ref:`object-event`
