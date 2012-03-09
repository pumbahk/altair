バックエンドからのイベント登録
=========================================

CMSはバックエンドからの通知を受けてイベントを登録、更新を行う。

通知のトリガは、バックエンド上でユーザがイベント登録を行ったタイミングで、
バックエンドからCMSにJSONオブジェクトをPOSTする形で通知する。

JSONオブジェクトは次のとおり。

.. code-block:: javascript

 {
   "created_at": "2012-01-10T13:42:00+09:00",
   "updated_at": "2012-01-11T15:32:00+09:00",
   "events": [
     {
       "id": 1,
       "name": "マツイ・オン・アイス",
       "start_on": "2012-03-15T19:00:00+09:00",
       "end_on": "2012-03-15T22:00:00+09:00",
       "performances": [
	 {
	   "id": 2,
	   "name": "マツイ・オン・アイス 東京公演",
	   "venue": "まついZEROホール",
	   "open_on": "2012-03-15T17:00:00+09:00",
	   "start_on": "2012-03-15T19:00:00+09:00",
	   "close_on": "2012-03-15T22:00:00+09:00",
	   "sales": [
	     {
	       "name": "presale",
	       "start_on": "2012-01-12T19:00:00+09:00",
	       "end_on": "2012-01-22T19:00:00+09:00",
	       "tickets": [
		 {
		   "name": "A席大人",
		   "seat_type": "A席",
		   "price": 5000
		 },
		 {
		   "name": "A席子供",
		   "seat_type": "A席",
		   "price": 3000
		 },
		 {
		   "name": "B席",
		   "seat_type": "B席",
		   "price": 3000
		 }
	       ]
	     },
	     {
	       "name": "normal",
	       "start_on": "2012-01-23T19:00:00+09:00",
	       "end_on": "2012-01-31T19:00:00+09:00",
	       "tickets": [
		 {
		   "name": "A席大人",
		   "seat_type": "A席",
		   "price": 5000
		 },
		 {
		   "name": "A席子供",
		   "seat_type": "A席",
		   "price": 3000
		 },
		 {
		   "name": "B席",
		   "seat_type": "B席",
		   "price": 3000
		 }
	       ]
	     }
	   ]
	 },
	 {
	   "id": 3,
	   "name": "マツイ・オン・アイス 大阪公演",
	   "venue": "心斎橋まつい会館",
	   "open_on": "2012-03-16T17:00:00+09:00",
	   "start_on": "2012-03-16T19:00:00+09:00",
	   "close_on": "2012-03-16T22:00:00+09:00",
	   "sales": [
	     {
	       "name": "presale",
	       "start_on": "2012-01-12T19:00:00+09:00",
	       "end_on": "2012-01-22T19:00:00+09:00",
	       "tickets": [
		 {
		   "name": "A席大人",
		   "seat_type": "A席",
		   "price": 5000
		 },
		 {
		   "name": "A席子供",
		   "seat_type": "A席",
		   "price": 3000
		 },
		 {
		   "name": "B席",
		   "seat_type": "B席",
		   "price": 3000
		 }
	       ]
	     },
	     {
	       "name": "normal",
	       "start_on": "2012-01-23T19:00:00+09:00",
	       "end_on": "2012-01-31T19:00:00+09:00",
	       "tickets": [
		 {
		   "name": "A席大人",
		   "seat_type": "A席",
		   "price": 5000
		 },
		 {
		   "name": "A席子供",
		   "seat_type": "A席",
		   "price": 3000
		 },
		 {
		   "name": "B席",
		   "seat_type": "B席",
		   "price": 3000
		 }
	       ]
	     }
	   ]
	 }
       ]
     }
   ]
 }

.. note:: end_onについて、パフォーマンス購入用URLについて https://dev.ticketstar.jp/redmine-altair/issues/181


イベント削除時は、deletedプロパティを付与したJSONオブジェクトPOSTする。
CMSはdeletedプロパティがtrueとなるパフォーマンス、チケット、イベントを削除する。

.. code-block:: javascript

 {
   "created_at": '2012-01-10T13:42:00+09:00',
   "updated_at": '2012-01-11T15:32:00+09:00',
   "events": [
     {
       "id": 1,
       "name": "マツイ・オン・アイス",
       "start_on": "2012-03-15T19:00:00+09:00",
       "end_on": "2012-03-15T22:00:00+09:00",
       "performances": [
	 {
	   "id": 2,
	   "deleted": true
	 }
       ]
     },
     {
       "id": 2,
       "deleted": true
     }
   ]
 }


API仕様
-------------------------

.. csv-table::

   API endpoint, /api/event/register
   プロトコル, HTTP 1.1
   リクエストメソッド, POST
   認証方式, X-Altair-AuthorizationヘッダにCMS上で予め登録済みのAPIKEYを付与してリクエストを行う。

