# altair.ticket_hub

TicketHubAPIとのコミュニケーター

## クラス

### TicketHubClient

実際にTicketHubシステムと通信するクラス。
認証、リクエスト作成、暗号化/複合化処理、レスポンス作成を担当。

### TicketHubAPI

各種TicktHubシステムからの情報取得、操作のためのIFの実装クラス。
TicketHubClientインスタンスを保持し、下記各種操作を実施。

#### ヘルスチェック healths

TicketHubシステムの死活監視をするためのメソッド

#### 施設情報取得 facility(id)

TicketHubシステムから任意の施設情報を取得するためのメソッド

#### 商品グループ情報取得 item_groups(facility_code, agent_code)

TicketHubシステムから任意の商品グループ情報を取得するためのメソッド

#### 商品情報取得 items(facility_code, agent_code, item_group_code)

TicketHubシステムから任意の商品情報を取得するためのメソッド

#### カート情報登録 create_cart(facility_code, agent_code, cart_items)

TicketHubシステムに任意の商品をカートに入れる(仮押さえ)ためのメソッド
レスポンスとしてcart_idが返ってくる

#### カート情報取得 cart(id)

TicketHubシステムから任意のカート情報を取得するためのメソッド

#### 仮注文情報登録 create_temp_order(cart_id)

TicketHubシステムに任意のカート情報で仮注文を入れるためのメソッド
仮注文をいれた時点では、実際の入場は不可。キャンセルは可能。
レスポンスとしてorder_noが返ってくる。

#### 注文情報確定登録 complete_order(order_no)

TicketHubシステムに任意の仮注文に対して注文確定するためのメソッド
注文確定をすることでQRコード入場が可能となる。またキャンセルは不可能となる。
