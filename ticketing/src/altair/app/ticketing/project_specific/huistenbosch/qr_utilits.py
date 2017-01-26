# -*- coding:utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta

import sqlahelper
from sqlalchemy.orm.session import object_session
from sqlalchemy.orm.exc import NoResultFound, UnmappedInstanceError

from pyramid.httpexceptions import HTTPNotFound

from altair.app.ticketing.core.models import TicketPrintHistory
from altair.app.ticketing.orders.api import get_order_by_order_no
from altair.app.ticketing.qr import get_qrdata_aes_builder
from altair.app.ticketing.qr.utils import (QRTicketObject,
                                           get_matched_token_from_token_id,
                                           get_or_create_matched_history_from_order,
                                           get_or_create_matched_history_from_token)

from . import (HT_TYPE_CODE,
               HT_ID_CODE,
               HT_COUNT_FLAG,
               HT_SEASON_FLAG,
               HT_SPECIAL_FLAG,
               HT_QR_DATA_HEADER,
               encrypting_items)

DBSession = sqlahelper.get_session()


def build_ht_qr_by_order_no(request, order_no, none_exception=HTTPNotFound):
    order = get_order_by_order_no(request, order_no)
    if order is None:
        raise none_exception
    return build_ht_qr_by_order(request, order)


def build_ht_qr_by_token_id(request, order_no, token_id, none_exception=HTTPNotFound):
    token = get_matched_token_from_token_id(order_no, token_id, none_exception=none_exception)
    return build_ht_qr_by_token(request, order_no, token)


def build_ht_qr_by_order(request, order):
    history = get_or_create_matched_history_from_order(order)
    return build_ht_qr_by_history(request, history)


def build_ht_qr_by_token(request, order_no, token):
    history = get_or_create_matched_history_from_token(order_no, token)
    return build_ht_qr_by_history(request, history)


def build_ht_qr_by_ticket_id(request, ticket_id):
    try:
        history = TicketPrintHistory \
            .filter_by(id=ticket_id) \
            .one()
        return build_ht_qr_by_history(request, history)
    except NoResultFound:
        return None


def build_ht_qr_by_history(request, history):
    data, ticket = make_data_for_qr(history)
    builder = get_qrdata_aes_builder(request)
    ticket.qr = builder.make(data)
    return ticket


def _get_db_session(history):
    try:
        return object_session(history)
    except UnmappedInstanceError:
        return DBSession


def make_data_for_qr(history):
    """
    'id_code': u'識別コード',
    'type_code': u'種別コード',
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

    _, params['ticket_code'], params['enterable_days'] = qr_ticket_obj.ordered_product_item.product_item.name.split('_')

    performance = qr_ticket_obj.performance

    params['valid_date_from'] = performance.open_on.strftime('%Y%m%d') if performance.open_on else '00000000'
    params['valid_date_to'] = performance.end_on.strftime('%Y%m%d') if performance.end_on else '00000000'
    params['enterable_from'] = performance.open_on.strftime('%H%M') if performance.open_on else '0000'
    usable_date_to = qr_ticket_obj.order.created_at + timedelta(days=90)
    params['usable_date_to'] = usable_date_to.strftime('%Y%m%d')
    params['issued_at'] = datetime.now().strftime('%Y%m%d')

    suffix = str(qr_ticket_obj.id)[:10]

    params['serial_no'] = 'A' + params['ticket_code'] + '0' * (10 - len(suffix)) + suffix

    data = dict(header=HT_QR_DATA_HEADER, content='')

    for item in encrypting_items:
        data['content'] += params[item]

    return data, qr_ticket_obj
