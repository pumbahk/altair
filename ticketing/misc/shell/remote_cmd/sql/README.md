# リモートSQL実行シェルスクリプト

データ抽出依頼のたびに行われる、

- 本番サーバーに入ってSQLの作成
- 結果出力ファイルをローカル環境までSCPで落とす
- Excelで開けるように文字コードをSJISに変換する

作業の短縮化、および過去に実行されたSQLの再利用を目的に作成しました。  
※ STANDBY_DBにしか接続しないため、SELECT文のSQLのみ実行してください。

ローカル環境から指定のリモート環境にSQLを実施し、結果はローカル環境のカレントディレクトリに取得されます。

## Setting

実行結果をExcelで開けるようにするため、nkfコマンドが必要です。  
Macの場合は以下を実行してインストールしてください。
```
brew nkf install
```


scriptディレクトリに実行したいSQLファイルを作成して置いてください。
（../common/config.shもスクリプト利用者の環境に合わせてください）

## Usage

実行コマンド:  
「bash <親ディレクトリまでのパス>/main.sh」  
→ 対話形式で処理が実行されます。SQL実行前に最終確認が表示されます。  

各スクリプトで「set -eu」を指定しているため、未定義の変数や、コマンドのリターンコードが失敗（1）になった場合は、処理が終了します。
デバッグ時は「bash -x」で起動してください。
