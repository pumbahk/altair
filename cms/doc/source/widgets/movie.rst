.. _widget-movie:

動画ウィジェット
============================

動画を表示するためのウィジェット。
管理画面で登録した動画を表示する。

CMS内で管理、生成を行い、テンプレートへの直接記述またはincludeファイルとする。
Ajaxでの呼び出しは行わない想定。

objectタグ / embedタグによりクライアントに直接描画する。

例:

.. code-block:: html

   <embed src="http://static.cms-ticketstar/file.wvx" type="application/x-mplayer2" autostart="false" width=320 height=285></embed>


動画ファイルの登録時、動画ファイルのヘッダをバリデーション対象とする。
容量、コーデックなどはバリデーションしない。

http://dev.ticketstar.jp/redmine-altair/issues/93


データ構造
----------------------

see also: :ref:`object-movie`
