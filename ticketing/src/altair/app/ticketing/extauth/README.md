extauth
=======

準備
---

1. extauth データベースの作成と extauth ユーザの作成
```
mysql> CREATE DATABASE extauth CHARSET=utf8;
mysql> GRANT ALL ON extauth.* TO extauth@127.0.0.1 IDENTIFIED BY 'extauth';
```
2. alembic
```
$ deploy/dev/bin/altair_alembic_paste -c deploy/dev/conf/altair.ticketing.extauth.ini upgrade head
$ deploy/dev/bin/altair_alembic_paste -c deploy/dev/conf/altair.ticketing.admin.ini upgrade head
```
3. buildout
```
$ (cd deploy/dev && ./buildout.sh)
```
4. supervisord の更新
```
$ deploy/dev/bin/supervisorctl
supervisorctl> reread
supervisorctl> update
supervisorctl> restart all
```
5. seed data の導入
```
$ sqlite3 deploy/dev/var/dummy_eagles_extauth_server/dummy_server.db < ticketing/src/altair/app/ticketing/extauth/dummy_server/seeds.sql
```

テンプレート
-----------

テンプレートは altair.app.ticketing.extauth:templates/ 配下にある。

ディレクトリ構造は以下のようになっている。

```
altair/app/ticketing/extauth/templates/
|
+- {organization.short_name}
|  |
|  +- {subtype}
|  |  |
|  |  +- base.mako (ベーステンプレート、以下のテンプレートはこのテンプレートをinherit)
|  |  |
|  |  +- index.mako (ランディング)
|  |  |
|  |  +- login.mako (ログイン画面)
|  |  |
|  |  +- select_account.mako (アカウント選択画面)
|  |  |
|  |  +- notfound.mako (404 「URLが正しくありません」)
|  |  |
|  |  +- fatal.mako (500 「致命的なエラーが発生しました」)
|  |
|  +- {subtype}
|  |  |
|  :  +- base.mako
|  :  :
|  |
|  +- __default__/
|     |
|     +- base.mako
|     |
|     +- index.mako
|     |
|     +- login.mako
|     |
|     +- select_account.mako
|     |
|     +- notfound.mako
|     |
|     +- fatal.mako
|
+- __default__/
:  |
:  +- {subtype}
:     |
:     +- ...
:
:

```

アセット
-------

アセット (画像、CSS、JavaScript) は altair.app.ticketing.extauth:static/ 配下にある。

ディレクトリ構造は以下のようになっている。

```
altair/app/ticketing/extauth/static/
|
+- {organization.short_name}
|  |
|  +- images/
|  |
|  +- css/
|  |
|  +- js/
|
+- {organization.short_name}
:  |
:  +- images/
:  :  
:
:
:

```

<h3>アセットのS3へのアップロード</h3>

```
$ deploy/dev/bin/s3cmd sync --exclude='*.swp' --recursive -P --no-preserve ticketing/src/altair/app/ticketing/extauth/static/ s3://tstar-dev/extauth/static/
```
