#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import sys

import transaction
import time
import sqlahelper

from datetime import datetime
from datetime import timedelta

from pyramid.paster import bootstrap, setup_logging

from altair.app.ticketing.skidata.exceptions import SkidataSendWhitelistError
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken
from altair.app.ticketing.core.models import (
    Organization, OrganizationSetting, Performance, Event, EventSetting,
    Product, ProductItem, Stock, StockType, Seat, SalesSegment, SalesSegmentGroup)
from altair.app.ticketing.skidata.models import (
    SkidataBarcode, SkidataProperty, SkidataPropertyTypeEnum, SkidataPropertyEntry)

from altair.skidata.sessions import skidata_webservice_session
from altair.skidata.api import make_whitelist
from altair.skidata.models import TSAction
from altair.skidata.models import TSOption
from altair.app.ticketing.skidata.api import send_whitelist_to_skidata

logger = logging.getLogger(__name__)

# 1000件としているのはSKIDATAが推奨する一回のリクエスト量です。
SKIDATA_SPLIT_COUNT = 1000


def _get_target_datetime(base_datetime, days, seconds=0):
    """
    If now time is 2019-11-07 10:22:25 and we input days as 1 and seconds as -1,
    we will get 2019-12-13 23:59:59 as result.
    :param days: plus days.
    :return:  example: 2019-12-13 23:59:59
    """
    dt = base_datetime.replace(hour=0, minute=0, second=0)
    dt = dt + timedelta(days=days, seconds=seconds)
    return dt


def _get_data_property(session, organization_id, related_id, prop_type):
    """
    紐付くSkidataPropertyを返却する。
    :param session: DBセッション。デフォルトはマスタ
    :return: 紐付くSkidataProperty
    """
    return session.query(SkidataProperty) \
        .join(SkidataPropertyEntry) \
        .filter(SkidataProperty.organization_id == organization_id) \
        .filter(SkidataProperty.prop_type == prop_type) \
        .filter(SkidataPropertyEntry.related_id == related_id) \
        .first()


def _get_data_property_value(prop_dict, session, organization_id, related_id, prop_type):
    key = str(organization_id) + '_' + str(related_id)
    property_value = prop_dict.get(key, None)
    if property_value is None:
        data_property = _get_data_property(session, organization_id, related_id, prop_type)
        property_value = data_property.value if data_property else None
        prop_dict[key] = property_value
    return property_value


def _get_current_milli_time():
    return int(round(time.time() * 1000))


def _add__query_columns(query):
    # pattern 1:
    return query.add_columns(SkidataBarcode.id.label('barcode_id'), SkidataBarcode.data)
    # pattern 2:
    #return query.add_columns(OrderedProductItemToken.id.label('token_id'))


def _get_barcode_id_and_data(whitelist_data):
    # pattern 1:
    return whitelist_data.barcode_id, whitelist_data.data
    # pattern 2:
    # barcode_obj = SkidataBarcode.find_by_token_id(whitelist_data.token_id, DBSession())
    # return barcode_obj.id if barcode_obj else None, barcode_obj.data if barcode_obj else None


def send_whitelist_data_to_skidata(argv=sys.argv):
    """Whitelist連携バッチ:連携対象データを送信
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    parser.add_argument('-offset', '--offset', metavar='offset', type=int, required=True,
                        help='Date unit:Period offset')
    parser.add_argument('-days', '--days', metavar='days', type=int, required=True,
                        help='Date unit:Period of data to be extracted')
    args = parser.parse_args(argv[1:])

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']
    session = get_global_db_session(registry, 'slave')
    skidata_session = skidata_webservice_session(registry.settings)

    # 多重起動防止
    LOCK_NAME = send_whitelist_data_to_skidata.__name__
    LOCK_TIMEOUT = 10
    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status != 1:
        logging.warn('lock timeout: already running process')
        return

    logger.info('start batch')

    # 引取方法がSKIDATA引取
    try:
        start_time = _get_current_milli_time()

        # Get data flow:
        # 1,Order->Organization->OrganizationSetting->OrganizationSetting.enable_skidata = 1
        # 2,Order->Performance->Event->EventSetting->EventSetting.enable_skidata = 1
        # 3,Order->OrderedProduct->Product->Product.name
        # 4,Order->OrderedProduct->OrderedProductItem->ProductItem->ProductItem.name
        # 5,Order->OrderedProduct->OrderedProductItem->OrderedProductItemToken->
        #   SkidataBarcode.data & [SkidataBarcode sent_at is NULL and canceled_at is NULL]
        # 6,Order->OrderedProduct->OrderedProductItem->OrderedProductItemToken->Seat.name
        # 7,Order->OrderedProduct->OrderedProductItem->ProductItem->Stock->StockType.name
        # 8,Order->[Order canceled_at is NULL and refunded_at is NULL and paid_at is not NULL]

        query = session.query(
            Order.order_no,
            Organization.id.label('organization_id'),
            Organization.code.label('organization_code'),
            Performance.open_on,
            Performance.start_on,
            StockType.name.label('stock_type_name'),
            StockType.attribute.label('gate_name'),
            Product.name.label('product_name'),
            ProductItem.id.label('product_item_id'),
            ProductItem.name.label('product_item_name'),
            Seat.id.label('seat_id'),
            Seat.name.label('seat_name'),
            SalesSegmentGroup.id.label('sales_segment_group_id'),
            SalesSegmentGroup.name.label('sales_segment_group_name')
        ) \
            .join(Organization, Organization.id == Order.organization_id) \
            .join(OrganizationSetting, OrganizationSetting.organization_id == Organization.id) \
            .join(Performance, Performance.id == Order.performance_id) \
            .join(Event, Event.id == Performance.event_id) \
            .join(EventSetting, EventSetting.event_id == Event.id) \
            .join(OrderedProduct, OrderedProduct.order_id == Order.id) \
            .join(Product, Product.id == OrderedProduct.product_id) \
            .join(SalesSegment, SalesSegment.id == Product.sales_segment_id) \
            .join(SalesSegmentGroup, SalesSegmentGroup.id == SalesSegment.sales_segment_group_id) \
            .join(OrderedProductItem, OrderedProductItem.ordered_product_id == OrderedProduct.id) \
            .join(ProductItem, ProductItem.id == OrderedProductItem.product_item_id) \
            .join(Stock, Stock.id == ProductItem.stock_id) \
            .join(StockType, StockType.id == Stock.stock_type_id) \
            .join(OrderedProductItemToken, OrderedProductItemToken.ordered_product_item_id == OrderedProductItem.id) \
            .outerjoin(Seat, Seat.id == OrderedProductItemToken.seat_id) \
            .join(SkidataBarcode, SkidataBarcode.ordered_product_item_token_id == OrderedProductItemToken.id) \
            .filter(OrganizationSetting.enable_skidata == 1) \
            .filter(EventSetting.enable_skidata == 1) \
            .filter(SkidataBarcode.canceled_at.is_(None)).filter(SkidataBarcode.sent_at.is_(None)) \
            .filter(Order.canceled_at.is_(None)).filter(Order.refunded_at.is_(None)) \
            .filter(Order.refund_id.is_(None)).filter(Order.paid_at.isnot(None))

        query = _add__query_columns(query)

        offset_days = args.offset
        delta_days = args.days
        now_datetime = datetime.now()
        start_datetime = _get_target_datetime(now_datetime, offset_days)
        end_datetime = _get_target_datetime(now_datetime, offset_days + delta_days, -1)

        whitelist_datas = query.filter(Performance.start_on.between(start_datetime, end_datetime)).all()
        logger.info('The target start date and time of Performance is between %s and %s.',
                    start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    end_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        all_data = []
        ssg_prop_dict = dict()
        pi_prop_dict = dict()

        for whitelist_data in whitelist_datas:
            # skidata plugin idの場合
            product_item_property_value = _get_data_property_value(pi_prop_dict, session,
                                                                   whitelist_data.organization_id,
                                                                   whitelist_data.product_item_id,
                                                                   SkidataPropertyTypeEnum.ProductItem.v)
            sales_segment_property_value = _get_data_property_value(ssg_prop_dict, session,
                                                                    whitelist_data.organization_id,
                                                                    whitelist_data.sales_segment_group_id,
                                                                    SkidataPropertyTypeEnum.SalesSegmentGroup.v)
            data_obj = _create_data_by_whitelist_data(whitelist_data,
                                                      product_item_property_value,
                                                      sales_segment_property_value)
            all_data.append(data_obj)

        _send_data_by_group(skidata_session, all_data)
        logger.info('It took %d millisecond for %d orders to be processed', (_get_current_milli_time() - start_time),
                    len(whitelist_datas))
    except Exception as e:
        logger.error(e)
        raise SkidataSendWhitelistError(
            'An unexpected error has occurred while fetching data and sending whitelist to HSH.')

    logger.info('end batch')


def _create_data_by_whitelist_data(whitelist_data, product_item_property_value, sales_segment_property_value):
    barcode_id, barcode_data = _get_barcode_id_and_data(whitelist_data)
    # Event ID は ORGコード + 公演の開演日時（YYYYmmddHHMM）
    skidata_event_id = u'{code}{start_date}'.format(code=whitelist_data.organization_code,
                                                    start_date=whitelist_data.start_on.strftime('%Y%m%d%H%M'))
    ts_option = TSOption(
        order_no=whitelist_data.order_no,
        open_date=whitelist_data.open_on,
        start_date=whitelist_data.start_on,
        stock_type=whitelist_data.stock_type_name,
        product_name=whitelist_data.product_name,
        product_item_name=whitelist_data.product_item_name,
        gate=whitelist_data.gate_name,
        seat_name=whitelist_data.seat_name if whitelist_data.seat_name else None,
        sales_segment=whitelist_data.sales_segment_group_name,
        ticket_type=sales_segment_property_value,
        person_category=product_item_property_value,
        event=skidata_event_id
    )
    # Whitelistのexpireは公演の開演年の12月31日 23:59:59
    expire = datetime(year=whitelist_data.start_on.year, month=12, day=31, hour=23, minute=59, second=59)
    whitelist_item = make_whitelist(action=TSAction.INSERT, qr_code=barcode_data, ts_option=ts_option, expire=expire)
    data_obj = dict(barcode_id=barcode_id, whitelist_item=whitelist_item)
    return data_obj


def _send_data_by_group(skidata_session, all_data):
    """send data by group.
    """
    split_data = [all_data[i:i + SKIDATA_SPLIT_COUNT] for i in range(0, len(all_data), SKIDATA_SPLIT_COUNT)]
    for data_objs in split_data:
        # タスクステータス更新
        transaction.begin()
        try:
            barcode_ids = []
            whitelist = []
            for data_obj in data_objs:
                barcode_ids.append(data_obj['barcode_id'])
                whitelist.append(data_obj['whitelist_item'])
            # barcode_listはSkidataBarcodeのリスト
            barcode_list = DBSession().query(SkidataBarcode).filter(SkidataBarcode.id.in_(barcode_ids)).all()
            send_whitelist_to_skidata(skidata_session, whitelist, barcode_list, fail_silently=True)
            transaction.commit()
        except Exception as e:
            transaction.abort()
            logger.error('we are continuing to send data for the next group!\n:%s', e.message)
