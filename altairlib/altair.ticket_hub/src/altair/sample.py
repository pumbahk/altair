# -*- coding: utf-8 -*-

from ticket_hub.api import TicketHubAPI

tickethub_base_uri = 'https://stg.webket.jp/tickethub/v9' # prod 'https://tickethub.webket.jp/'
seller_code = '06006' # 事業者コード
seller_channel_code = '0011' # 事業者チャネルコード
api_key = 'lQ1SDy' # 認証キー
api_secret = 'Cpy*t^6^d}b' # パスワード

client = TicketHubAPI(
    base_uri=tickethub_base_uri,
    api_key=api_key,
    api_secret=api_secret,
    seller_code=seller_code,
    seller_channel_code=seller_channel_code
)
