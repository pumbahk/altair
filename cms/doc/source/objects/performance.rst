.. _object-performance:

パフォーマンスオブジェクト
-----------------------------------

イベント内のパフォーマンスを表すオブジェクト。

.. code-block:: python

 {
     'performance': {
         'event_id': int, # event ID
         'title': unicode, # パフォーマンス名
         'performance_open': datetime, # パフォーマンス開始日時
         'performance_close': datetime, # パフォーマンス終了日時
     }
 }

see also: :ref:`object-event`
