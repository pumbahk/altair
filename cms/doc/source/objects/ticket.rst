.. _object-ticket:

券種オブジェクト
-----------------------------

.. code-block:: python

   {
       'ticket': {
           'event_id': str, # イベントID
           'performance_id': str, # パフォーマンスID
           'seattype': object, # 席種
           'seat': object, # 席在庫
           'title': unicode, # チケットの名前
           'type': unicode, # 券種
           'price': int, # 価格
           'url': str, # チケットを表すURLのパーマリンク
       }
   }

see also: :ref:`object-seat`, :ref:`object-event`
