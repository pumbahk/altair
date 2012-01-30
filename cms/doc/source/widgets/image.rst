.. _widget-image:

画像ウィジェット
============================

http://dev.ticketstar.jp/redmine-altair/issues/118

データはCMSに保持しストレージはS3を使用する。
S3へのアクセスはCloudFrontを経由して行い、クライアントへのデータ転送時間を短縮する。

CMS内で管理、生成を行い、テンプレートへの直接記述またはincludeファイルとする。
Ajaxでの呼び出しは行わない想定。

.. image:: ../images/image.png


アセットに保存されたメタデータを元に、次のようなHTMLを出力する。

.. code-block:: html

 <img src="http://static.ticketstar/images/blueman.jpg" width="320" height="240" alt="ブルーマンついに千秋楽決定!"/>


データ構造
----------------

see also: :ref:`object-image`
