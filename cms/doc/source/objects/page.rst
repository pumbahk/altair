.. _object-page:

ページオブジェクト
---------------------------------

ページを表示するにあたって必要な情報を保持したオブジェクト。
フロント側のビュー表示に用いる。

.. code-block:: python

 {
     'page': {
         'id': int, # ページID
         'event_id': int, # イベントID
         'title': unicode, # ページタイトル
         'description': unicode, # ページの説明
         'keyword': unicode, # ページのキーワード文字列
         'parent_page_id': int, # 親となるページのID（nullable）
         'tag_ids': list, # タグのID
         'layout_id': unicode, # レイアウトのID
         'structure': { # レイアウトファイルのDIV IDをキーとして、配置するウィジェットをリストで保持する。
             'div-identifier': [int, int],
             'div-identifier': [int, int]
         }
     }
 }
