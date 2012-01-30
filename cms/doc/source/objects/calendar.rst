.. _object-calendar:

カレンダオブジェクト
------------------------------

カレンダを描画するために必要なオブジェクトを定義する。
イベントの配列内の定義は :ref:`object-event` を参照すること。

カレンダ情報はデータ量が多いことが予想されるため月単位で処理を行う想定。

.. code-block:: python

 {
     'calendar': {
         'month': 2012,
         'events': list, # イベントオブジェクトの一覧を含める
     }
 }

see also: :ref:`object-event`
