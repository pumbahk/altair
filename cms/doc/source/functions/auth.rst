ユーザ認証
==========================

サイト利用時の、ログイン、ログアウト機能を提供する。


認証方式
------------------

基本的にはOpenIDを利用する。6月版では楽天ID認証を実装する（OAuth）。
CMSアカウントとフロントエンドの間では、セッションは共有しない（それぞれ個別にログインする必要がある）。


OpenIDの楽天ID認証を使う予定

.. note:: その他サイトのOpenIDも使えたら良いなあ


楽天ID認証
========================================

* OAuthを使用する

「OpenIDWithOAuth技術資料Ver20100810.doc」を参照する。

:"openID version": OpenID2.0

.. todo:: GETかPOSTか表記

関連issue
* http://dev.ticketstar.jp/redmine-altair/issues/85


提供される機能
----------------------------------------

+ ユーザ認証機能（必須）
+ ユーザ認証結果確認機能（必須）
+ OAuthアクセストークン取得機能(オプション)
+ OAuth API呼び出し機能 （オプション）


ワークフロー
----------------------------------------

.. seqdiag::

   seqdiag {
	 user [label="ユーザ"];
	 site [label="提携サイト"];
	 if [label="楽天認証I/F"];
	 auth [label="認証システム"];

     user -> if [label= "1. 認証要求"]
     if -> if [label=サイトのチェック];
     if -> auth [label="認証要求"];
     user <- auth[label="楽天ID/パスワード要求"];

     === 楽天OpenIDログイン ===

     user -> auth [label="ログイン"];
        
     if <- auth[label="認証結果"];
     site <- if [label="1. 認証結果(OpenID引数確認)"];
     site -> if [label="2. 認証確認要求"];
     site <- if [label="2. 認証可否"];
     user <- site[label="ログインOK"];

     === 販売サイトログイン ===

     user -> site[label="販売サイトにログイン"];

     site -> if [label="3. アクセストークン取得要求"];
     site <- if [label="3. アクセストークン返却"];

     site -> if [label="4. API実行要求"];
     site <- if [label="4. API実行結果"];
   }


1. 認証要求
----------------------------------------

request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

認証url::

  https://api.id.rakuten.co.jp/openid/auth?{$parameter}={$value}

.. csv-table:: request paramaters
   :header: パラメータ名, 説明, 指定内容もしくは例
   :widths:   15,20,20

   openid.ns,   "固定値",   "http://specs.openid.net/auth/2.0"
   openid.return_to,   "戻り先URL",   "(例) http://www.example.com/"
   openid.claimed_id,   "固定値",   "http://specs.openid.net/auth/2.0/identifier_select"
   openid.identity,   "固定値",   "http://specs.openid.net/auth/2.0/identifier_select"
   openid.mode,   "固定値",   "checkid_setup"
   openid.ns.oauth,   "固定値",   "http://specs.openid.net/extenstions/oauth/1.0"
   openid.oauth.consumer,   "別途ご連絡する固定値",   "akfjakldjfakldjfkalsdjfklasdjfklajdf"
   openid.oauth.scope,   "認証後に利用したい機能",   "rakutenid_basicinfo, rakutenid_contactinfo"


.. note:: 

   openid.return_toは、楽天側の認証フロー終了後にリダイレクトされるURL。(事前に申請したurlで待ち受けることになる)
   事前にcallback用のURLと楽天に申請しておく必要がある。

リクエスト例::

  https://api.id.rakuten.co.jp/openid/auth?
        openid.ns=http://specs.openid.net/auth/2.0&
        openid.return_to=http://www.example.com/&
        openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select&
        openid.identity=http://specs.openid.net/auth/2.0/identifier_select&
        openid.mode=checkid_setup&
        openid.ns.oauth=http://specs.openid.net/extenstions/oauth/1.0&
        openid.oauth.consumer=XXXXXXXXXXXXX&
        openid.oauth.scope=rakutenid_basicinfo,rakutenid_contactinfo

response
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::  Reponse
   :header: "パラメータ名", "説明", "内容もしくは例"
   :widths: 10,10,25

   "openid.ns", "固定値", "http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
   "openid.op_endpoint", "固定値", "https%3A%2F%2Fapi.id.rakuten.co.jp%2Fopenid%2Fauth"
   "openid.claimed_id", "ユーザーのOpenID", "https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7nzC2SulpKTnGlWg%3D"
   "openid.response_nonce", "認証時の現在時刻にプレフィックスをつけた一意な値", "2008-09-04T04%3A58%3A20Z0"
   "openid.mode", "固定値", "id_res"
   "openid.identity", "ユーザーのOpenID", "https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7nzC2SulpKTnGlWg%3D"
   "openid.return_to", "戻り先URL", "(例) http%3A%2F%2Fwww.example.com%2F"
   "openid.assoc_handle", "トランザクションキー", "ce1b14fb7941fcd9"
   "openid.signed", "署名に使用したパラメーター名", "op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle"
   "openid.sig", "BASE64エンコードした署名の値", "xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw%3D"
   "openid.ns.oauth", "固定値", "http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0"
   "openid.oauth.request_token", "リクエストトークン", "fadfajdfajdfklajdfkljafklsdjfklasjfkladjfklaj"
   "openid.oauth.scope", "認証後に利用したい機能", "rakutenid_basicinfo%2Crakutenid_contactinfo"

POSTで返ってくる。

.. note:: openid.identity(openid.claimed_id)が、ユーザのOpenID

.. note:: モバイルの場合、文字コード「S-JIS」でPOSTデータで結果が返却

response例 ::
  
   http://www.example.com/?
      openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&
      openid.op_endpoint=https%3A%2F%2Fapi.id.rakuten.co.jp%2Fopenid%2Fauth&
      openid.claimed_id=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7C2SulpKTnGlWg%3D&
      openid.response_nonce=2008-09-04T04%3A58%3A20Z0&
      openid.mode=id_res&
      openid.identity=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7nzC2SulpKTnGlWg%3D&
      openid.return_to=http%3A%2F%2Fwww.example.com%2F&
      openid.assoc_handle=ce1b14fb7941fcd9&
      openid.signed=op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle&
      openid.sig=xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw%3D&
      openid.ns.oauth=http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0&
      openid.oauth.request_token=XXXXXXXXXXXXX&
      openid.oauth.scope=rakutenid_basicinfo%2Crakutenid_contactinfo


2. 認証結果確認(verify)
----------------------------------------

要求APIのレスポンスのopenid.identityの値をurlデコードし利用する。::

  opened.identity = https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7nzC2SulpKTnGlWg%3D
         ↓ URLデコード
  https://myid.rakuten.co.jp/openid/user/9Whpri7nzC2SulpKTnGlWg=

"9Whpri7nzC2SulpKTnGlWg="がuniqな文字列。


認証結果確認要求URL::

  https://api.id.rakuten.co.jp/openid/auth?{$parameter}={$value}…

.. csv-table::  Request
   :header: "パラメータ名", "説明", "内容もしくは例"
   :widths: 10,10,25

   "openid.ns", "戻り値", "http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
   "openid.op_endpoint", "戻り値", "https%3A%2F%2Fapi.id.rakuten.co.jp%2Fopenid%2Fauth"
   "openid.claimed_id", "戻り値", "(例)　https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7C2SulpKTnGlWg%3D"
   "openid.response_nonce", "戻り値", "(例)　2008-09-04T04%3A58%3A20Z0"
   "openid.mode", "固定値", "check_authentication"
   "openid.identity", "戻り値", "(例)　https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7C2SulpKTnGlWg%3D"
   "openid.return_to", "戻り値", "(例)　http%3A%2F%2Fwww.example.com%2F"
   "openid.assoc_handle", "戻り値", "(例)　ce1b14fb7941fcd9"
   "openid.signed", "戻り値", "(例)　op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle"
   "openid.sig", "戻り値", "(例)　xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw%3D"
   "openid.ns.oauth", "固定値", "http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0"
   "openid.oauth.request_token", "リクエストトークン", "fadfajdfajdfklajdfkljafklsdjfklasjfkladjfklaj"
   "openid.oauth.scope", "認証後に利用したい機能", "（例）rakutenid_basicinfo%2Crakutenid_contactinfo"

.. note:: openid.mode こちら側で指定する何らかの固定値らしい。

リクエスト例::

   https://api.id.rakuten.co.jp/openid/auth?
      openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&
      openid.op_endpoint=https%3A%2F%2Fapi.id.rakuten.co.jp%2Fopenid%2Fauth&
      openid.claimed_id=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7C2SulpKTnGlWg%3D&
      openid.response_nonce=2008-09-04T04%3A58%3A20Z0&
      openid.mode=check_authentication&
      openid.identity=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7nzC2SulpKTnGlWg%3D&
      openid.return_to=http%3A%2F%2Fwww.example.com%2F&
      openid.assoc_handle=ce1b14fb7941fcd9&
      openid.signed=op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle&
      openid.sig=xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw%3D&
      openid.ns.oauth=http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0&
      openid.oauth.request_token=XXXXXXXXXXXXX&
      openid.oauth.scope=rakutenid_basicinfo%2Crakutenid_contactinfo

response
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. csv-table::  Response
   :header: "パラメータ名", "説明", "内容もしくは例"
   :widths: 10,10,25

   is_valid, 可否, "ture：成功, false：失敗"
   Ns, 固定値, http://specs.openid.net/auth/2.0


レスポンス例:: 

  is_valid:true
  ns:http://specs.openid.net/auth/2.0

3. アクセストークン取得API
----------------------------------------

アクセストークン要求URL::

  https://api.id.rakuten.co.jp/openid/oauth/accesstoken?{$parameter}={$value}…

Request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::  Request
   :header: "パラメータ名", "説明", "内容もしくは例"
   :widths: 10,10,25

   oauth_consumer_key, 固定値, partner0001
   oauth_token, リクエストトークン, fadfajdfajdfklajdfkljafklsdjfklasjfkladjfklaj
   oauth_signature_method, 固定値, "HMAC-SHA1 （現在のところ対応している署名形式はHMAC-SHA1だけです）"
   oauth_timestamp, 現在時刻, "(例)　 1262925659115 1970年1月1日からの経過ミリ秒"
   oauth_nonce, ユニークな任意の値, "(例)　testetstestetstetetsteste リクエスト毎にユニークな値となるようにしてください。 (複数リクエスト間で同じ値を使いまわさないでください。)"
   oauth_version, 固定値, 1.0
   oauth_signature, 署名, "提携サイト様の署名を指定してください。 署名についてはhttp://oauth.net/core/1.0a/#anchor46を参照ください"

.. note:: oauth_nonceはリクエスト毎にユニークな値にする必要がある。

.. note:: 全てのパラメータはURLエンコードする

リクエスト例:

  https://api.id.rakuten.co.jp/openid/oauth/accesstoken?
  oauth_consumer_key=testconsumer&
  oauth_nonce=1262925659115&
  oauth_signature_method=HMAC-SHA1&
  oauth_timestamp=1262925659115&
  oauth_token=197a576948a4832928d0b56903c9b495&
  oauth_version=1.0&
  oauth_signature=t1424NQwJJ%2F%2BlI088xLBOzvlZfY%3D

Response
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::  Response
   :header: "パラメータ名", "説明", "内容もしくは例"
   :widths: 10,10,25

   oauth_token, アクセストークン, fafjfdjfjfsdjfslkdjflaksjd
   oauth_token_secret, トークンシークレット, fafjfdjfjfsdjfslkdjflaksjd

レスポンス例:: 

   oauth_token:fafjfdjfjfsdjfslkdjflaksjd
   oauth_token_secret:fjlkjfajdfkafjalkdjfklsja


4. OAuth APIアクセス機能
----------------------------------------

APIアクセスURL::

  https://api.id.rakuten.co.jp/openid/oauth/call?{$parameter}={$value}…

Request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::  Request
   :header: "パラメータ名", "説明", "内容もしくは例"
   :widths: 10,10,25

   oauth_consumer_key, 固定値, partner0001
   oauth_token, アクセストークン, fadfajdfajdfklajdfkljafklsdjfklasjfkladjfklaj
   oauth_signature_method, 固定値, "HMAC-SHA1 （現在のところ対応している署名形式はHMAC-SHA1だけです）"
   oauth_timestamp, 現在時刻, "(例)　 12629256591151970年1月1日からの経過ミリ秒"
   oauth_nonce, ユニークな任意の値, "(例)　testetstestetstetetsteste リクエスト毎にユニークな値となるようにしてください。(複数リクエスト間で同じ値を使いまわさないでください。)"
   oauth_version, 固定値, 1.0
   rakuten_oauth_api, API名, rakutenid_basicinfo
   oauth_signature, 署名, "提携サイト様の署名を指定してください。 署名についてはhttp://oauth.net/core/1.0a/#anchor46を参照ください"

リクエスト例::

  https://api.id.rakuten.co.jp/openid/oauth/call?
  oauth_consumer_key=testconsumer&
  oauth_nonce=1262925659115&
  oauth_signature_method=HMAC-SHA1&
  oauth_timestamp=1262925659115&
  oauth_token=197a576948a4832928d0b56903c9b495&
  oauth_version=1.0&
  rakuten_oauth_api=rakutenid_basicinfo&
  oauth_signature=t1424NQwJJ%2F%2BlI088xLBOzvlZfY%3D

.. note:: oauth_nonceはリクエスト毎にユニークな値にする必要がある。

.. note:: 全てのパラメータはURLエンコードする

Response
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

APIのレスポンスは各API毎に異なる。

利用するAPI
----------------------------------------
(OAuthAPI一覧Ver20100715.docから利用するであろうAPIのみを抜粋)

ユーザ基本情報取得API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:API名: rakutenid_basicinfo
:機能: ログインユーザのニックネーム、氏名、生年月日、性別を取得
:URL: https://api.id.rakuten.co.jp/openid/oauth/call?rakuten_oauth_api=rakutenid_basicinfo

レスポンス形式::

  status_code:SUCCESS
  emailAddress:rakutaro@mail.rakuten.co.jp
  nickName:テストユーザ０００１
  firstName:鈴木
  lastName:楽太郎
  firstNameKataKana:スズキ
  lastNameKataKana:ラクタロウ
  birthDay:1981/10/26
  sex:男性

楽天ポイント取得API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:API名: rakutenpoint_api
:機能: ログインユーザの楽天ポイントを取得
:URL: https://api.id.rakuten.co.jp/openid/oauth/call?rakuten_oauth_api=rakutenpoint_api&nameofapi=simpleget

.. note::  リクエストパラメータに「nameofapi=simpleget」を付与してください

レスポンス形式::

  2310,21,0,4,7500

.. note:: （[確定ポイント数,仮ポイント数,期間限定ポイント数,ランク,キャッシュ数]という並びで結果が返ります）


Task
----------------------------------------

.. note::

   return_toのURLを楽天に知らせる必要がある。

   "5-1. 実装する際のお願いより
   事前に本資料3ページの「3-1.ユーザー認証機能　リクエストパラメータ」内の「openid.return_to」パラメーターに指定する戻りURLを弊社にお知らせ下さい。
   提携サイト様からのアクセスが可能になるよう、弊社側で設定をしたします。
   ※予めご連絡をいただき、弊社側で登録したURL以外はご利用いただけませんのでご注意下さい。"とのこと

.. note::

   ログインボタンの形に決まりがある。

   """
     【ログインボタンに関して】
   ボタン画像とウェブサイト上の文言、画像などの要素の間には、最低20ピクセル以上の幅を
   確保してください。
   ボタン画像を提携サイト様へのログイン以外の目的で利用することはご遠慮ください。
   ボタン画像を編集し、サイズ、デザインを変更して利用することはご遠慮ください。
   提供したボタン画像以外の画像を利用すること、また、提携サイト様が独自にログインフォームやリンクを作成するのはご遠慮ください。
   """

::

  misato:

  テスト環境、詳細なところは来週中(1/16週)内に楽天の担当者と調整予定
  IDServiceに楽天OpenIDの中で内部的に使われていますが、こちらからは特に意識する必要はありません。

  OpenIDによる認証と、認証後個人情報を取得するためのAPIとポイント取得APIを利用することなると思います。
