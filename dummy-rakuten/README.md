# dummy-rakuten

## What's this?
* 楽天ログイン関係のモックです.
* IDとパスワードを入力するログイン画面、OpenIDを得るためのAPI、Oauthで個人情報やポイント番号を得るためのAPIを提供します.
* HTTPSサーバまたはHTTPサーバとして動きます.

## Requirement
* openssl, nodejs, npm が必要です.

## Setup
依存ライブラリをインストールします.

```
npm install
```

HTTPSサーバとして動かす場合、まず、秘密鍵と証明書を作ります. ファイル名がデフォルトと異なる場合は、index.jsの起動時に指定してください. ファイルが存在しない等の場合は、特にエラーは出さず、HTTPサーバとして起動します.

```
openssl req -batch -new -key server_key.pem -out server_csr.pem -subj "/C=JP/ST=Tokyo/L=Setagaya/O=TicketStar/OU=Dev/CN=dummy-rakuten.jp"
openssl x509 -in server_csr.pem -out server_crt.pem -req -signkey server_key.pem -days 73000 -sha256
```

起動します.

```
node index.js --port 8443 --base https://dummy-rakuten.jp:8443 -k server_key.pem -c server_crt.pem
```

* portオプションで、listenするポートを指定します.
* baseオプションで、リダイレクトURLを生成する際のprefixを指定します.

## Customize
* user.jsを書き換えると、IDに応じて異なるユーザ情報を返すことができます.
* session.jsを書き換えると、少しだけまともなセッション管理ができるかもしれません.

## Limitation
* 認証サーバとしてのセキュリティは一切確保されません. OAuthの署名やトークンの生成なども適当です.

## Tips
* Pythonで、不正な証明書のHTTPSサーバに強引に接続したい場合は、以下のコードを追加.
```
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```
