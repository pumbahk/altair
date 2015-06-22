Famiポート運用ツール
====================

セットアップ
------------

```
% deploy/dev/bin/altair_alembic_paste -c deploy/dev/conf/altair.famiport.ini upgrade head
```


初期ユーザの作り方
------------------

`altair_pshell_famiport` を使う

```
>>> from altair.app.ticketing.famiport.optool.api import create_user
>>> create_user(request, 'admin', 'admin', 'administrator')
```
