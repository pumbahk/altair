# -*- coding: utf-8 -*-

from collections import OrderedDict

# 固定値の設定（現時点2017-01-12,仮数値として設定する。）
HT_QR_DATA_HEADER = '6'
HT_TYPE_CODE = '6'
HT_ID_CODE = 'HTB0000001'
HT_COUNT_FLAG = '1'
HT_SEASON_FLAG = '1'
HT_SPECIAL_FLAG = '0'

# 自由エリア
HT_QR_DATA_FREE = 'http://huistenbosch.tstar.jp/'.ljust(40)


ja_map = {
    'id_code': u'識別コード',
    'type_code': u'種類コード',
    'ticket_code': u'券種コード',
    'serial_no': u'通し番号',
    'issued_at': u'発行日',
    'count_flag': u'カウントフラグ',
    'season_flag': u'シーズンフラグ',
    'valid_date_from': u'有効期限From',
    'valid_date_to': u'有効期限To',
    'enterable_days': u'入場期限',
    'enterable_from': u'入場可能時間',
    'usable_date_to': u'使用期限', #購入日＋90日
    'special_flag': u'特殊フラグ'
}

item_list = OrderedDict([
    ('id_code', 10),
    ('type_code', 1),
    ('ticket_code', 6),
    ('serial_no', 17),
    ('issued_at', 8),
    ('count_flag', 1),
    ('season_flag', 1),
    ('valid_date_from', 8),
    ('valid_date_to', 8),
    ('enterable_days', 3),
    ('enterable_from', 4),
    ('usable_date_to', 8),
    ('special_flag', 1)
])

encrypting_items =[
    'id_code',
    'type_code',
    'ticket_code',
    'serial_no',
    'issued_at',
    'count_flag',
    'season_flag',
    'valid_date_from',
    'valid_date_to',
    'enterable_days',
    'enterable_from',
    'usable_date_to',
    'special_flag'
]