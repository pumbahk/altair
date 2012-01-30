.. _object-twitter-usertimeline:

Twitterユーザタイムラインオブジェクト
-------------------------------------------

Twitterの特定のユーザのtweetを描画するためのオブジェクト。
Twitterのscren nameを保持し、その情報を利用してウィジェットで描画を行う想定。
:ref:`object-twitter-search` と似ているが、こちらは特定のユーザのtweetのみを取り扱う。

.. code-block:: python

 {
     'twitter': {
         'title': unicode, # オブジェクトの名称
         'screen_name': str # Twitter screen name
     }
 }

see also: :ref:`object-twitter-search`

see also: :ref:`widget-twitter-search`, :ref:`widget-twitter-usertimeline`
