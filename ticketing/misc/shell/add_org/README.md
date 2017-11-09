# ORG追加シェルスクリプト

ORG追加時に使用するシェルスクリプト群。

[ templates.sh, s3_upload.sh ]  
「02_テンプレートの作成 https://confluence.rakuten-it.com/confluence/pages/viewpage.action?pageId=776251923」に該当。  
templates.shでテンプレートの作成を自動化、s3_upload.shでアップロードします。

[ dns_lb_setting.sh ]
「10_ORGの作業履歴 > <各ORG名> > 「DNS, LB設定（PRを作ってinfraに依頼）」の項目」に該当

[ fmp_db_insert.sh ]
「【作業手順】DBへのFamiport関連データ追加作業テンプレート https://confluence.rakuten-it.com/confluence/pages/viewpage.action?pageId=811681188」に該当  

[ fmp_image_upload.sh ]
「【作業手順】Famiportへ画像FTP送信手順テンプレート https://confluence.rakuten-it.com/confluence/pages/viewpage.action?pageId=816554101」に該当

## Setting

各ORG追加手順の「管理画面ADMIN権限ユーザで実施」がブラウザ上で完了していることを前提とします。  
config.shに追加したいORGの設定内容を書き換えてください。  
（../common/config.shもスクリプト利用者の環境に合わせてください）

[ templates.sh, s3_upload.sh ]  
"PATH_TO_MB_LOGO"で指定する画像は.gifに変換済みであることを確認してください。
変換には以下のようなサービスもあります。

オンラインコンバータ
https://convertio.co/ja/gif-png/

[ fmp_db_insert.sh, fmp_image_upload.sh ]  
以下の「Box 各ORGディレクトリ https://rak.app.box.com/folder/6339643229」と  
依頼時に渡される画像をひとまとめにしてください。  
また、ファイル名の"FP_TENANT_CODE"を合わせておいてください。

## Usage

実行コマンド:  
「bash <add_orgディレクトリまでのパス> 上記いずれかのシェルスクリプト名」  
設定確認画面や、実行内容の確認などが適宜表示されていくので、指示に従ってください。

各スクリプトで「set -eu」を指定しているため、未定義の変数や、コマンドのリターンコードが失敗（1）になった場合は、処理が終了します。

デバッグ時は「bash -x」で起動してください。
