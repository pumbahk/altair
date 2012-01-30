.. _object-freetext:

フリーテキストオブジェクト
---------------------------------

フリーテキストを保持するオブジェクト。プレインテキストやHTMLなど、中身のデータ形式は問わない。

.. code-block:: python

 {
     'freetext': {
         'title': unicode, # オブジェクトの名称
         'text': unicode # 描画するHTMLコード
     }
 }

see also: :ref:`widget-freetext`
