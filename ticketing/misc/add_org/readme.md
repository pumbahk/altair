# ORG追加シェルスクリプト

ORG追加時に使用するシェルスクリプト群。

[ templates.sh, s3_upload.sh ]  
「02_テンプレートの作成 https://confluence.rakuten-it.com/confluence/pages/viewpage.action?pageId=776251923」に該当。  
templates.shでテンプレートの作成を自動化、s3_upload.shでアップロードします。

[ dns_lb_setting.sh ]
「10_ORGの作業履歴 > <各ORG名> > 「DNS, LB設定（PRを作ってinfraに依頼）」の項目」に該当  

## Setting

config.shに追加したいORGの設定内容を書き換えてください。
"PATH_TO_MB_LOGO"で指定する画像は.gifに変換済みであることを確認してください。
変換には以下のようなサービスもあります。

オンラインコンバータ
https://convertio.co/ja/gif-png/

## Usage

実行コマンド:  
「bash <add_orgディレクトリまでのパス> 上記いずれかのシェルスクリプト名」  
設定確認画面や、実行内容の確認などが適宜表示されていくので、指示に指示に従ってください。

## Credits

Motoi Komatsu

## License

株式会社楽天チケットスター Rakuten Ticketstar.Inc
