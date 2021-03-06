レイアウトテンプレート管理
===============================

http://dev.ticketstar.jp/redmine-altair/issues/90

レイアウトテンプレートの管理を行う。

HTMLテンプレートは、アプリケーションデプロイと同時に更新される。
CMS上での登録、削除は行わない想定。

テンプレートは、ベーステンプレート、ページテンプレートの二種類に分けて管理を行う。

ベーステンプレートは「楽天チケット」などの、元サイトのデザインを選択するものとする。
ページテンプレートは、ウィジェットのレイアウト情報を持つファイルで、数種類の中から選択するものとする。

例えば、

* 楽天用ベーステンプレート + 2カラムページテンプレート
* チケットスター独自サイトのベーステンプレート + 3カラムページテンプレート

などという組み合わせで使用する。

例:

.. blockdiag::

   diag {
       orientation = portrait;
       楽天テンプレート -> 2カラムページテンプレート;
       楽天テンプレート -> 3カラムページテンプレート;

       ほげほげ社テンプレート -> 全画面ページテンプレート;
   }
