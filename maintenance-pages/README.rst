メンテナンスページ
==================

Apache + PHP な感じです。

ポート 7999 で listen します。

Host ヘッダを見て出し分けをするので、フロントのプロキシから必ずヘッダを渡すようにしてください。


ファイル構成
------------

::

  maintenance-pages/
  |
  +- docroots/ (各クライアント用メンテナンスページ)
  |  |
  |  +- #common/ (共通コンテンツ)
  |  |  |
  |  |  +- _htaccess (htaccessファイル)
  |  |  |
  |  |  +- body.php (告知内容をここに書く)
  |  |
  |  +- 89ers/
  |  |  |
  |  |  +- assets/ (画像等格納ディレクトリ)
  |  |
  |  +- NH/
  |  |  |
  |  |  +- assets/ (画像等格納ディレクトリ)
  |  |
  |  +- CR/
  |     |
  |     +- assets/ (画像等格納ディレクトリ)
  |
  +- mapping/ (ドメイン名とクライアントのマッピング)
  |  |
  |  +- 89ers.tstar.jp -> ../docroots/89ers (シンボリックリンク)
  |  |
  |  +- happinets.tstar.jp -> ../docroots/NH (シンボリックリンク)
  |  |
  |  +- tokyo-cr.tstar.jp -> ../docroots/CR (シンボリックリンク)
  |  |
  |  :
  |
  +- etc/ (設定ファイル)
  |  |
  |  +- httpd.conf
  |
  +- var/
  |  |
  |  +- run/
  |  |  |
  |  |  +- pid (プロセスのpid)
  |  |  |
  |  |  +- lock (accept lock)
  |  |
  |  +- log/
  |     |
  |     +- access.log (アクセスログ)
  |     |
  |     +- error.log (エラーログ)
  | 
  +- run.sh (起動用シェルスクリプト)

起動/停止方法
-------------

Mac OS X::

  $ HTTPD=/usr/sbin/httpd MODULE_DIR=/usr/libexec/apache2 MIME_TYPE_FILE=/etc/apache2/mime.types ./run.sh start|stop

Debian / Ubuntu::

  $ HTTPD=/usr/sbin/apache2 MODULE_DIR=/usr/lib/apache2/modules MIME_TYPE_FILE=/etc/mime.types ./run.sh start|stop

