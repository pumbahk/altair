.. _object-facebook:

フェイスブックオブジェクト
--------------------------------

Facebookページのタイムラインを表示するためのオブジェクト。
FacebookページのURLを保持し、その情報を元にウィジェットで描画する想定。

.. code-block:: python

 {
     'facebook': {
         'title': unicode, # Facebookページの名前
         'url': str # FacebookページのURL
     }
 }


see also: :ref:`widget-facebook`
