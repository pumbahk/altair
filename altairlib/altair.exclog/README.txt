.. contents::

使い方
============

設定
-----------------

::

  include('altair.exclog')

::

  [loggers]
  root, ticketing, exclog

  [exclog_logger]
  qualname = altair.exclog
  level = ERROR


設定値
---------------

- altair.exclog.extra_info [default = true]  trueの場合はログメッセージにenviron, paramsの情報を追加します
- altair.exclog.show_traceback [default = false] trueの場合はレスポンスボディにログメッセージを表示します
- altair.exclog.ignored [default = (WSGIHTTPException,)] 無視すべき例外クラスを指定します
