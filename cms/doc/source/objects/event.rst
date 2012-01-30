.. _object-event:

イベントオブジェクト
-------------------------------

イベント情報を表すオブジェクト。

.. code-block:: python

 {
     'event': {
         'id': str, # イベントID
         'ticket_ids': list, # チケットIDが入る。複数あり。
         'seat_ids': list, # 席種ID。複数あり。
         'seatfigure_ids': int, # 座席表ID
         'client_id': int, # 販売者
         'inquiry_for': unicode, # 問い合わせ先文字列
         'title': unicode, # イベントタイトル
         'subtitle': unicode, # イベントサブタイトル
         'place': unicode, # 会場名
         'description': unicode, # イベント内容
	 'options': list, # オプションサービス(ファンクラブ限定、託児サービス)
         'event_open': datetime, # イベントの開催開始日
         'event_close': datetime, # イベントの開催終了日
         'deal_open': datetime, # チケット販売開始日
         'deal_close': datetime, # チケット販売終了日
     }
 }

see also (object): :ref:`object-ticket`, :ref:`object-seatfigure`, :ref:`object-client`, :ref:`object-performance`

see also (widget): :ref:`widget-countdown`
