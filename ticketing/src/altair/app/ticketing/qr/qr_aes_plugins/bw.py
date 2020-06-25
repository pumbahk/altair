# -*- coding:utf-8 -*-

import logging
logger = logging.getLogger(__name__)

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


BW_TICKET_SEQ = '001'
BW_UNIQUE_FLAG = '1'
BW_VALID_FROM = '00000000'
BW_VALID_TO = '00000000'

encrypting_items =[
    'type_code',
    'location_code',
    'ticket_code',
    'ticket_qty',
    'ticket_seq',
    'unique_flag',
    'issued_at',
    'valid_form',
    'valid_to'
]

DBSession = get_session()


def _get_db_session(history):
    try:
        return object_session(history)
    except UnmappedInstanceError:
        return DBSession


def includeme(config):
    config.add_qr_aes_plugin(BWQRAESPlugin("BELGIAN_BEER_WEEKEND_2020_IS_FUN"), u"BW")
    config.scan(__name__)


def get_type_code(qr_ticket_obj):
    product = qr_ticket_obj.product
    if not qr_ticket_obj.product:
        # 一括発券だとproductが取れないため
        product = qr_ticket_obj.order.items[0].product
    if product.name.count(u"STARTER"):
        return u"RAKSTR"
    if product.name.count(u"GROUP"):
        return u"RAKGRP"
    if product.name.count(u"LOUNGE"):
        return u"RAKLNG"
    if product.name.count(u"PARTY"):
        return u"BBWGAL"
    return u""


def get_location_code(performance):
    if performance.name.count(u'Nagoya'):
        return u"NGY"
    if performance.name.count(u'Yokohama'):
        return u"YKH"
    if performance.name.count(u'Osaka'):
        return u"OSK"
    if performance.name.count(u'Sapporo'):
        return u"SAP"
    if performance.name.count(u'Hibiya'):
        return u"HBY"
    if performance.name.count(u'Kobe'):
        return u"KBE"
    if performance.name.count(u'Tokyo'):
        return u"TKY"
    return u""


@implementer(IQRAESPlugin)
class BWQRAESPlugin(QRAESPlugin):
    def __init__(self, key=None):
        super(BWQRAESPlugin, self).__init__(key)

    def make_data_for_qr(self, history):
        """
        type_code(string 6):チケット種類コード
        location_code(string 3):場所コード
        ticket_code(string 12):注文番号（一意）
        ticket_qty(string 3):注文枚数 001-999
        ticket_seq(string 3):同じ注文で複数の席種があるときのシーケンス番号（連番）001-999
        unique_flag(bool 1):Falseの場合は、同じticket_codeを持つチケットを複数回使用できます。
        issued_at(date 8):発行日 YYYYMMDD
        valid_from(date 8):有効期限開始日 YYYYMMDD
        valid_to(date 8):有効期限終了日 YYYYMMDD
        """

        qr_ticket_obj = QRTicketObject(history, _get_db_session(history))

        params = dict()

        type_code = get_type_code(qr_ticket_obj)
        params['type_code'] = type_code
        params['location_code'] = get_location_code(qr_ticket_obj.performance)
        params['ticket_code'] = qr_ticket_obj.order_no
        params['ticket_qty'] = str(qr_ticket_obj.order.items[0].quantity).rjust(3, '0')
        params['ticket_seq'] = BW_TICKET_SEQ
        params['unique_flag'] = BW_UNIQUE_FLAG
        params['issued_at'] = qr_ticket_obj.order.created_at.strftime("%Y%m%d")
        if type_code == u"BBWGAL":
            # TKT-8424
            params['valid_form'] = '20190910'
            params['valid_to'] = '20190910'
        else:
            # 公演日だけ使えるように変更 TKT-10252
            start_on_str = qr_ticket_obj.order.performance.start_on.strftime("%Y%m%d")
            params['valid_form'] = start_on_str
            params['valid_to'] = start_on_str

        data = dict(header='', content='')

        for item in encrypting_items:
            data['content'] += params[item]
        return {'data': data, 'ticket': qr_ticket_obj}

    def output_to_template(self, ticket):
        # TODO orderreview
        return dict(
            order=ticket.order,
            ticket=ticket,
            performance=ticket.performance,
            event=ticket.event,
            product=ticket.product
        )