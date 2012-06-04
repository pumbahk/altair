ログイン認証
========================================

http://dev.ticketstar.jp/redmine-altair/issues/124

クライアントは次の2段階のフローでCMSの利用を開始する。

* バックエンドへのアカウント登録

 #. クライアントはチケットスタートの契約を済ませる
 #. チケットスターがバックエンドへ、クライアント情報の登録とアカウント発行を行う
 #. チケットスターがクライアントへ、ログイン先URL、アカウント情報（サイト管理者の認証情報）を連絡する

* CMSの利用登録

 #. クライアントはチケットスターから受領した情報を元にCMSページを開く
 #. CMSとバックエンドの間で認証を行う（OpenID. CMSがConsumer, バックエンドがServiceProvidor）


バックエンドへの登録:

.. seqdiag::

   sequence {
     client => ticketstar [label = "contract"] {
       ticketstar => backend [label = "register client"];
     }
     ticketstar -> client [label = "send account information"];
   }

CMS利用開始（バックエンドへのOAuth）:

.. seqdiag::

   sequence {
     browser => CMS [label = "view login page", return = "login page"];

     browser => CMS [label = "click login button"] {
       CMS => backend [label = "request token url", return = "response"];
     }
     browser => backend [label = "request authentication url", return = "response (with callback url)"];
     browser => CMS [label = "request callback", return = "response"];
   }


イベントを登録する
=================================

イベントの登録は次のフローで行う。販売者とサイト管理者は同じオペレータが行う想定。

#. 販売者がバックエンドに新しいイベントを登録する
#. 販売者がバックエンドでCMSへの同期リクエストを要求する
#. バックエンドはCMSのイベント作成APIを呼び出す
#. CMS上にイベントが作成される

.. seqdiag::

   seqdiag {
     seller => backend [label = "register new event"] {
       backend => CMS [label = "create new event via WebAPI"];
     }
     seller => CMS [label = "edit event detail"];
   }


関連issue

* http://dev.ticketstar.jp/redmine-altair/issues/104
* https://dev.ticketstar.jp/redmine-altair/issues/176



イベントを検索して編集する
================================

.. note:: フロントではなく、CMS内の検索
.. todo:: 検索、絞り込みの対象を確認する。

イベントの検索バリエーションは以下のとおり。

* カテゴリからの絞り込み
* 一覧から参照（時系列）
* 検索

 * タイトル、本文
 * 開催期間


.. seqdiag::

   seqdiag {
     browser => CMS [label = "reqeust with search query", return="search result"];
   }


関連ページの一覧・編集
-----------------------------

イベントのページを作成することが出来る。
イベントに対するアクションは次のとおり。

+ イベントに関連するページ作成/編集
+ 登録済みページ一覧（選択すると編集）


ページの編集
-----------------------------

ページは以下の項目を編集することが出来る。

+ URL
+ ページ名
+ 説明
+ キーワード
+ ページレイアウト
+ ページ内容
+ 公開／非公開
+ 編集可能なオペレータ

ページ内容は、特定のページレイアウトに対し、ブロック（HTMLのブロック）単位でウィジェットを配置することで表現する。


サイトマップ
-----------------------

TBD

関連issue
* https://dev.ticketstar.jp/redmine-altair/issues/119



特集ページ
-----------------------

現行の楽天チケットの特集ページは、静的ページとして実現する。

関連issue

* https://dev.ticketstar.jp/redmine-altair/issues/103
* https://dev.ticketstar.jp/redmine-altair/issues/183


ページ作成・編集
===============================

CMSは少なくとも次のようなページを管理する（詳細はTBD）。

* トップページ
* カテゴリトップ
* イベント検索(ディレクトリツリー)
* イベント詳細(商品詳細)
* 特集ページ
* 公演変更中止情報
* サイトマップ
* メルマガ管理（subject, body, 送信対象, 配信スケジュール）
* マイページ
* お問い合わせ
* チケットエージェント
* メルマガ
* 予約画面、キャンセル待ち

.. note::

   お問い合わせはsalesforceを利用する。
   salesforceへリンクを行うのみで、具体的な実装はなし。
   http://dev.ticketstar.jp/redmine-altair/issues/127

.. note::

   決済系はまとめて作業をしたほうが良さそう
   お隣キープは、決済処理の実装が終わってから
   **おとなりキープは2012/7版では実装しない**
