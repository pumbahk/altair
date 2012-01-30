CMSの利用を開始する
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

http://dev.ticketstar.jp/redmine-altair/issues/104

前提条件::

 フロントエンドCMSがイベント登録用のAPIを持つ

イベントの登録は次のフローで行う。販売者とサイト管理者は同じオペレータが行う想定。

#. 販売者がバックエンドに新しいイベントを登録する
#. バックエンドはCMSのイベント作成APIを呼び出す
#. CMS上でイベントの下書きが作成される


.. seqdiag::

   seqdiag {
     seller => backend [label = "register new event"] {
       backend => CMS [label = "create new event via WebAPI"];
     }
     seller => CMS [label = "edit event detail"];
   }


フロントエンドCMSにAPIを用意し、バックエンドでイベント登録時にこのAPIを呼ぶ
バックエンド側で公演登録に連動して販売ページもできるようなUIを想定している。

イベント登録時に以下の情報を管理する。

:event_name: イベント名
:tag: タグ (many, optional)
:category: カテゴリ
:visibility:  公開範囲
:sale_term:  販売期間(開始〜終了)
:performance_term: 開催期間(開始〜終了)

.. note:: 登録データの内容についてはまだ詰めてない


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


関連ページを編集する
-----------------------------

ここで選べるメニューは

+ イベントトップページ作成/編集
+ 登録されているページの一覧(選択すると編集)
+ 更新変更中止情報
+ アセット管理
+ その他のページ作成

.. note:: アセット管理は、イベント単位で行う想定。
.. note:: イベントトップページは必須。それ以外のページは任意の想定


ページを追加する
-----------------------------

ページの作成では

+ ページレイアウト
+ ページ名
+ 公開範囲
+ 内容

を設定できれば良いと思う。

内容の中にwidgetを埋め込むイメージ。


サイトマップ
-----------------------

https://dev.ticketstar.jp/redmine-altair/issues/119

TBD


特集ページ
-----------------------

https://dev.ticketstar.jp/redmine-altair/issues/103

TBD


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
* 購入画面

   * 決済
   * お隣キープ

.. note::

   お問い合わせはsalesforceを利用する。
   salesforceへリンクを行うのみで、具体的な実装はなし。
   http://dev.ticketstar.jp/redmine-altair/issues/127

.. note:: チケットエージェントについて確認
.. note:: メルマガについて確認。ユーザ側管理画面？
.. note:: チケットエージェント、メルマガは後回し

.. note::

   決済系はまとめて作業をしたほうが良さそう
   お隣キープは、決済処理の実装が終わってから
   **おとなりキープは2012/7版では実装しない**

.. note:: とりあえず、トップページと特集ページ、ヘルプは後回し。テキストが登録できる程度のものにする
.. note:: メルマガ配信はCMSとは分けて検討する
.. note:: 特集ページは普通のページとして取り扱う


ページ毎の編集権限
-----------------------------

各ページが編集かどうかはユーザロールによって異なる。
想定しているページの編集可否は以下のとおり。

.. csv-table::
   :header: , CMS管理者, サイト管理者

   トップページ, ◯, ×
   カテゴリトップ, ◯, ×
   イベント検索, ◯, ×
   イベント詳細, ◯, ◯
   特集ページ, ◯, ？
   公園変更中止情報, ◯, ◯
   サイトマップ, ◯, ×
   メルマガ管理, ◯, ◯


----

サイト管理者の管理
========================================

* http://dev.ticketstar.jp/redmine-altair/issues/100
* http://dev.ticketstar.jp/redmine-altair/issues/120

チケットスターにより作成されたアカウント（サイト管理者）は、サイトを管理する別のアカウントを作成することが出来る。
クライアント情報は常に1以上のサイト管理者を有する。

.. blockdiag::

   diagram {
     orientation = portrait;

     group {
       クライアント情報（会社情報） -> サイト管理者A;
     }

     クライアント情報（会社情報） -> サイト管理者A;
     サイト管理者A -> サイト管理者B [label="追加"];
   }


