.. _object-order-history:

購入履歴オブジェクト
-------------------------------

.. code-block:: javascript

 {
     'order-history': [ // 過去の購入情報を必要な分リストで保持する
         {
             'order': {
                 'datetime': datetime, // 購入した日付
                 'event': event_object, // イベントオブジェクト
             },
         }
     ]
 }

see: :ref:`object-event`
