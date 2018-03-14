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


BW_UNIQUE_FLAG = '1'
BW_VALID_FROM = '00000000'
BW_VALID_to = '00000000'

encrypting_items =[
    'type_code',
    'location_code',
    'ticket_code',
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
    config.add_qr_aes_plugin(BWQRAESPlugin("BELGIAN_BEER_WEEKEND_2018_IS_FUN"), u"BW")
    config.add_qr_aes_delivery_form_maker(BWQRAESDeliveryFormMaker(), u"BW")
    config.scan(__name__)


def get_type_code(product):
    if product.name.count("STARTER"):
        return "RAKSTR"
    if product.name.count("GROUP"):
        return "RAKGRP"
    return ""


def get_location_code(performance):
    if performance.name.count('Nagoya'):
        return "NGY"
    if performance.name.count('Yokohama'):
        return "YKH"
    if performance.name.count('Osaka'):
        return "OSK"
    if performance.name.count('Sapporo'):
        return "SAP"
    if performance.name.count('Hibiya'):
        return "HBY"
    if performance.name.count('Kobe'):
        return "KBE"
    if performance.name.count('Tokyo'):
        return "TKY"
    return ""


@implementer(IQRAESPlugin)
class BWQRAESPlugin(QRAESPlugin):
    def __init__(self, key=None):
        super(BWQRAESPlugin, self).__init__(key)

    def make_data_for_qr(self, history):
        """
        type_code(string 6):チケット種類コード
        location_code(string 3):場所コード
        ticket_code(string 12):注文番号（一意）
        ticket_seq(string 3):同じ注文で複数枚のチケットがあるときのシーケンス番号（連番）001-999
        unique_flag(bool 1):Falseの場合は、同じticket_codeを持つチケットを複数回使用できます。
        issued_at(date 8):発行日 YYYYMMDD
        valid_from(date 8):有効期限開始日 YYYYMMDD 必ず00000000を入れる
        valid_to(date 8):有効期限終了日 YYYYMMDD 必ず00000000を入れる
        """

        qr_ticket_obj = QRTicketObject(history, _get_db_session(history))
        params = dict()

        params['type_code'] = get_type_code(qr_ticket_obj)
        params['location_code'] = get_location_code(qr_ticket_obj.performance)
        params['ticket_code'] = qr_ticket_obj.order_no
        params['ticket_seq'] = str(qr_ticket_obj.item_token.serial+1).rjust(3, '0')
        params['unique_flag'] = BW_UNIQUE_FLAG
        params['issued_at'] = qr_ticket_obj.order.created_at
        params['valid_form'] = BW_VALID_FROM
        params['valid_to'] = BW_VALID_to

        data = dict(header='', content='')

        for item in encrypting_items:
            data['content'] += params[item]
        return {'data': data, 'ticket': qr_ticket_obj}

    def output_to_template(self, ticket):
        allow_sp = ticket.order.payment_delivery_method_pair.delivery_method.preferences.get(
            unicode(QR_AES_DELIVERY_PLUGIN_ID), {}).get(u'qr_aes_allow_sp', False)
        # TODO orderreview
        return dict(
            order=ticket.order,
            ticket=ticket,
            performance=ticket.performance,
            event=ticket.event,
            product=ticket.product,
            allow_sp=allow_sp
        )