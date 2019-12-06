#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import sys

import sqlahelper
import transaction
import time

from datetime import datetime
from datetime import timedelta

from pyramid.paster import bootstrap, setup_logging

from altair.app.ticketing.skidata.scripts.exceptions import SkidataBatchErrorException
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken
from altair.app.ticketing.core.models import (
    Organization, OrganizationSetting, Performance, Event, EventSetting,
    Product, ProductItem, Stock, StockType, Seat, SalesSegment, SalesSegmentGroup)
from altair.app.ticketing.skidata.models import (
    SkidataBarcode, SkidataProperty, SkidataPropertyTypeEnum, SkidataPropertyEntry)

logger = logging.getLogger(__name__)

# 多重起動防止
LOCK_TIMEOUT = 10

# 1000件としているのはSKIDATAが推奨する一回のリクエスト量です。
LOCK_NAME = __name__
SKIDATA_SPLIT_COUNT = 1000


def _get_target_datetime(base_datetime, days):
    """
    If now time is 2019-11-07 10:22:25 and we input days as 1,
    we will get 2019-11-08 00:00:00 as result.
    :param days: plus days.
    :return:  example: 2019-11-08 00:00:00
    """
    if days == 0:
        return base_datetime
    dt = base_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    dt = dt + timedelta(days=days)
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


def send_white_list_data_to_skidata(argv=sys.argv):
    """Whistlist連携バッチ:連携対象データを送信
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

    logger.info('start batch')

    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status != 1:
        logger.warn('lock timeout: already running process')
        return

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
            ProductItem.original_product_item_id.label('original_product_item_id'),
            ProductItem.name.label('product_item_name'),
            OrderedProductItemToken.id.label('token_id'),
            Seat.id.label('seat_id'),
            Seat.name.label('seat_name'),
            SalesSegmentGroup.id.label('sales_segment_group_id'),
            SalesSegmentGroup.name.label('sales_segment_group_name'),
            SkidataBarcode.id.label('skidata_barcode_id')
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
            .filter(Order.canceled_at.is_(None)).filter(Order.refunded_at.is_(None)).filter(Order.paid_at.isnot(None))

        offset_days = args.offset
        delta_days = args.days
        now_datetime = datetime.now()
        start_datetime = _get_target_datetime(now_datetime, offset_days)
        end_datetime = _get_target_datetime(now_datetime, offset_days + delta_days)

        white_list_datas = query.filter(Performance.open_on.between(start_datetime, end_datetime)).all()
        logger.info('start_datetime=%s,end_datetime=%s', start_datetime, end_datetime)

        all_data = []
        ssg_prop_dict = dict()
        pi_prop_dict = dict()

        for white_list_data in white_list_datas:
            # skidata plugin idの場合
            ssg_prop_value = _get_data_property_value(ssg_prop_dict, session, white_list_data.organization_id,
                                                      white_list_data.sales_segment_group_id,
                                                      SkidataPropertyTypeEnum.SalesSegmentGroup.v)
            # 抽選からオーダーを作ると、original_product_item_idになりました。
            product_item_id = white_list_data.original_product_item_id if white_list_data.original_product_item_id \
                else white_list_data.product_item_id
            pi_prop_value = _get_data_property_value(pi_prop_dict, session, white_list_data.organization_id,
                                                     product_item_id,
                                                     SkidataPropertyTypeEnum.ProductItem.v)
            white_list_data = _create_data_by_white_list_data(white_list_data, ssg_prop_value, pi_prop_value)
            all_data.append(white_list_data)

        _send_data_by_group(all_data, now_datetime)

        logger.info('pattern 1: using %d millisecond for %s count within %s orders',
                    (_get_current_milli_time() - start_time), len(all_data), len(white_list_datas))
    except Exception as e:
        raise SkidataBatchErrorException('pattern 2: {}'.format(e.message))

    conn.close()
    logger.info('end batch')


def _create_data_by_white_list_data(white_list_data, ssg_prop_value, pi_prop_value):
    barcode_obj = SkidataBarcode.find_by_token_id(white_list_data.token_id, DBSession())
    qr_obj = dict(
        data=barcode_obj.data,
        order_no=white_list_data.order_no,
        open_on=white_list_data.open_on,
        start_on=white_list_data.start_on,
        stock_type_name=white_list_data.stock_type_name,
        product_name=white_list_data.product_name,
        product_item_name=white_list_data.product_item_name,
        gate=white_list_data.gate_name,
        seat_name=white_list_data.seat_name if white_list_data.seat_name else None,
        sales_segment_group_name=white_list_data.sales_segment_group_name,
        ssg_property_value=ssg_prop_value,
        pi_property_value=pi_prop_value,
        EVENT=white_list_data.organization_code+white_list_data.start_on.strftime("%Y%m%d%H%M")  # SKIDATA EVENT
    )

    white_list_obj = dict(
        skidata_barcode_id=barcode_obj.id,
        qr_obj=qr_obj
        )
    return white_list_obj


def _send_data_by_group(all_data, now_datetime):
    """send data by group.
    """
    logger.info('pattern 1:all data is %s count', len(all_data))
    split_data = [all_data[i:i + SKIDATA_SPLIT_COUNT]
                  for i in range(0, len(all_data), SKIDATA_SPLIT_COUNT)]
    for data_objs in split_data:
        logger.info('pattern 1: sent data: %s', len(data_objs))
        # タスクステータス更新
        transaction.begin()
        try:
            barcode_objs = []
            qr_objs = []
            for data_obj in data_objs:
                barcode_objs.append(data_obj['skidata_barcode_id'])
                qr_objs.append(data_obj['qr_obj'])
            _prepare_barcode_data(barcode_objs, now_datetime)
            _send_qr_objs_to_hsh(qr_objs)
            transaction.commit()
        except Exception as e:
            transaction.abort()
            logger.error('we are continuing to send data for the next group!\n:%s', e.message)


def _prepare_barcode_data(barcode_ids, now_datetime):
    barcode_objs = DBSession().query(SkidataBarcode) \
        .filter(SkidataBarcode.id.in_(barcode_ids))
    barcode_objs.update({SkidataBarcode.sent_at: now_datetime}, synchronize_session=False)


def _send_qr_objs_to_hsh(qr_objs):
    # TODO Send qr_obj to HSH service.
    pass
