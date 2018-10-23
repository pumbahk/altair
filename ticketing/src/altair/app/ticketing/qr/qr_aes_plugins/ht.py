# -*- coding:utf-8 -*-

import logging

from collections import OrderedDict
from datetime import timedelta
from zope.interface import implementer

from sqlahelper import get_session
from sqlalchemy.orm.session import object_session
from sqlalchemy.orm.exc import UnmappedInstanceError

from altair.app.ticketing.payments.plugins import QR_AES_DELIVERY_PLUGIN_ID
from altair.app.ticketing.qr.interfaces import IQRAESPlugin
from altair.app.ticketing.qr.qr_aes_plugins.base import QRAESPlugin
from altair.app.ticketing.qr.utils import QRTicketObject

logger = logging.getLogger(__name__)

# HTのカスタマイズ内容
# HBの実装はHTQRAESPluginを継承して行った
## 固定値の設定（現時点2017-07-13。）
HT_QR_DATA_HEADER = '6'
HT_TYPE_CODE = '6'
HT_ID_CODE = 'HTB0000001'
HT_COUNT_FLAG = '1'
HT_SEASON_FLAG = '0'
HT_SPECIAL_FLAG = '0'

## 自由エリア
HT_QR_DATA_FREE = 'http://huistenbosch.co.jp/event/'.ljust(40)


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

DBSession = get_session()

def _get_db_session(history):
    try:
        return object_session(history)
    except UnmappedInstanceError:
        return DBSession

def includeme(config):
    config.add_qr_aes_plugin(HTQRAESPlugin(), u"HT")

@implementer(IQRAESPlugin)
class HTQRAESPlugin(QRAESPlugin):
    def __init__(self, key=None):
        super(HTQRAESPlugin, self).__init__(key)

    def make_data_for_qr(self, history):
        """
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
        """

        qr_ticket_obj = QRTicketObject(history, _get_db_session(history))
        params = dict()

        params['type_code'] = HT_TYPE_CODE
        params['id_code'] = HT_ID_CODE
        params['count_flag'] = HT_COUNT_FLAG
        params['season_flag'] = HT_SEASON_FLAG
        params['special_flag'] = HT_SPECIAL_FLAG

        _, ticket_code, enterable_days, usable_days = qr_ticket_obj.ordered_product_item.product_item.name.split('_')

        params['ticket_code'] = ticket_code
        params['enterable_days'] = enterable_days.strip()[:3].rjust(3, '0')

        performance = qr_ticket_obj.performance

        params['valid_date_from'] = performance.open_on.strftime('%Y%m%d') if performance.open_on else '0' * 8
        params['valid_date_to'] = performance.end_on.strftime('%Y%m%d') if performance.end_on else '0' * 8
        params['issued_at'] = performance.start_on.strftime('%Y%m%d') if performance.start_on else '0' * 8
        if performance.open_on:
            params['enterable_from'] = performance.open_on.strftime('%H%M')
        else:
            params['enterable_from'] = performance.start_on.strftime('%H%M') if performance.start_on else '0' * 4
        usable_date_to = qr_ticket_obj.order.created_at + timedelta(days=int(usable_days))
        params['usable_date_to'] = usable_date_to.strftime('%Y%m%d')

        suffix = str(qr_ticket_obj.id)[:10]
        params['serial_no'] = 'A' + params['ticket_code'] + suffix.rjust(10, '0')

        data = dict(header=HT_QR_DATA_FREE + HT_QR_DATA_HEADER, content='')

        for item in encrypting_items:
            data['content'] += params[item]

        return {'data': data, 'ticket': qr_ticket_obj}

    def output_to_template(self, ticket):
        # TODO: 2018年7月の頭にスマホ禁止のテンプレート廃止する
        allow_sp = ticket.order.payment_delivery_method_pair.delivery_method.preferences.get(
            unicode(QR_AES_DELIVERY_PLUGIN_ID), {}).get(u'qr_aes_allow_sp', False)

        return dict(
            order=ticket.order,
            ticket=ticket,
            performance=ticket.performance,
            event=ticket.event,
            product=ticket.product,
            allow_sp=allow_sp
        )