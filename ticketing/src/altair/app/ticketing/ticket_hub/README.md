# TicketHub document

## マスタデータ

### TicketHubFacility

TicketHubの施設情報。Altairのイベントに相当。
メールベースでグッドフェローズ担当者より手動連携されてくるフローを想定しており、販売前にAltairDBに登録する必要あり。

※データ自体はTicketAPIより取得することも可能。TicketHUB_IF_API仕様書、施設情報取得参照

### TicketHubItemGroup

TicktHubの商品グループ情報。Altairの席種に相当。
メールベースでグッドフェローズ担当者より手動連携されてくるフローを想定しており、販売前にAltairDBに登録する必要あり。

※データ自体はTicketAPIより取得することも可能。TicketHUB_IF_API仕様書、商品グループ情報取得参照

### TicketHubItem

TicktHubの商品情報。Altairの商品に相当。
メールベースでグッドフェローズ担当者より手動連携されてくるフローを想定しており、販売前にAltairDBに登録する必要あり。

※データ自体はTicketAPIより取得することも可能。TicketHUB_IF_API仕様書、商品情報取得参照

## 取引データ

### TicketHubOrder

TicktHubの注文商品情報。AltairのOrderに相当。
引取方法に`TICKET_HUB_DELIVERY_PLUGIN`が設定された販売区分の商品が注文された際に作成されるデータ。

|状態|cart_no|order_no|completed_at|備考|
|:--|:--|:--|:--|:--|
|カート(一時的に在庫確保)|あり|null|null|Cart生成時に同時に生成される|
|仮注文(決済まで完了済み。キャンセル可)|あり|あり|null|Order生成時に仮注文状態に状態遷移|
|注文確定(入場可。キャンセル不可)|あり|あり|あり|バッチ処理(scripts/complete_ticket_hub_orders.py)によって注文確定状態に状態遷移|

### TicketHubOrderedTicket

TicktHubの注文商品明細情報。AltairのTicketに相当。
TicketHub側に仮注文リクエストした際に作成されるデータ。
施設入場のためのQRコードデータを含む(ユーザは購入履歴画面でQRコードを閲覧可能)。
