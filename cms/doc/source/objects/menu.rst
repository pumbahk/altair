.. _object-menu:

メニューオブジェクト
---------------------------

メニュー表示するためのオブジェクト。

.. code-block:: python

 {
     'menutab': [
         {'url': str, 'label': unicode},
         {'url': str, 'label': unicode},
         {'url': str, 'label': unicode} # urlが無ければリンクなし
     ]
 }

.. note:: Menuモデルなどを作成して、表示させるタブを編集させる想定。

see also: :ref:`widget-menu`
