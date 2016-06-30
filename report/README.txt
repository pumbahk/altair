イーグルスの販売データ抽出用の各種スクリプト
=====================================

環境：dbrp1.1a
自分のhomeディレクトリにvirtualenvを作りpymysqlとwootheeをinstallする
pythonスクリプトはvirtualenv下のpythonを使って実行する

概要：
create_order.sql, create_order_seat.sqlを用いて予め必要なテーブルを作成しておく
テーブル名と対象のイベントはその都度確認する
ref.
select_order.py, select_item.py
sql_select_per_orderのEvent.id, Performance.start_onの条件
order_table_name, order_seat_table_name

select_order.py, select_item.pyの順に本番のticketing DBから必要なデータをローカルのreport DBに読み込む

select_seat_choice.bash, order_select.sql, update_order_select_type.pyは購入時の座席選択の有無データが必要な場合のみ使用
2016年6月時点では使用していない

select_result.sqlを用いてローカルのreport DBから依頼されたデータを出力する

