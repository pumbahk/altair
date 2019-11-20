# -*- coding: utf-8 -*-
import argparse
import logging
import sqlahelper
import transaction
import time

from datetime import datetime
from datetime import timedelta

from pyramid.paster import bootstrap, setup_logging

from altair.sqlahelper import get_db_session
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken
from altair.app.ticketing.core.models import (
    Organization, OrganizationSetting, Performance, Event, EventSetting,
    Product, ProductItem, Stock, StockType, Seat, SeatAttribute,
    PaymentDeliveryMethodPair, DeliveryMethod, SalesSegment, SalesSegmentGroup)
from altair.app.ticketing.skidata.models import (
    SkidataBarcode, SkidataProperty, SkidataPropertyTypeEnum, SkidataPropertyEntry)
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID, SKIDATA_QR_DELIVERY_PLUGIN_ID

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
    dt = base_datetime.replace(minute=0, hour=0, second=0, microsecond=0)
    dt = dt + timedelta(days=days)
    return dt


def _get_gate_name(session, seat_id):
    if seat_id is None:
        return ''
    gate_attribute = session.query(SeatAttribute)\
        .filter(SeatAttribute.seat_id == seat_id)\
        .filter(SeatAttribute.name == 'gate').first()
    return gate_attribute.value if gate_attribute else ''


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
    property_value = prop_dict[key] if key in prop_dict else None
    if property_value is None:
        data_property = _get_data_property(session, organization_id, related_id, prop_type)
        property_value = data_property.value if data_property else ''
        prop_dict[key] = property_value
    return property_value


current_milli_time = lambda: int(round(time.time() * 1000))


def send_white_list_data_to_skidata():
    """Whistlist連携バッチ:連携対象データを送信
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('-offset', '--offset', metavar='offset', type=int, required=True)
    parser.add_argument('-days_delta', '--days_delta', metavar='days_delta', type=int, required=True)
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    session = get_db_session(request, 'slave')

    logger.info('send_white_list_data_to_skidata: start batch')

    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status != 1:
        logger.warn('lock timeout: already running process')
        return

    # 引取方法がSKIDATA引取
    try:
        # TODO for test
        start_time = current_milli_time()

        # Get data flow:
        # 1,Order->Organization->OrganizationSetting->OrganizationSetting.enable_skidata = 1
        # 2,Order->Performance->Event->EventSetting->EventSetting.enable_skidata = 1
        # 3,Order->PaymentDeliveryMethodPair->DeliveryMethod->
        #   DeliveryMethod.delivery_plugin_id in [SEJ_DELIVERY_PLUGIN_ID, SKIDATA_QR_DELIVERY_PLUGIN_ID]
        # 4,Order->OrderedProduct->Product->Product.name
        # 5,Order->OrderedProduct->OrderedProductItem->ProductItem->ProductItem.name
        # 6,Order->OrderedProduct->OrderedProductItem->OrderedProductItemToken->
        #   SkidataBarcode.data & [SkidataBarcode sent_at is NULL and canceled_at is NULL]
        # 7,Order->OrderedProduct->OrderedProductItem->OrderedProductItemToken->Seat.name
        # 8,Order->OrderedProduct->OrderedProductItem->ProductItem->Stock->StockType.name
        # 9,Order->[Order canceled_at is NULL and refunded_at is NULL and paid_at is not NULL]

        query = session.query(
            Order.order_no,
            Organization.id.label('organization_id'),
            Performance.open_on,
            Performance.start_on,
            StockType.name.label('stock_type_name'),
            Product.name.label('product_name'),
            ProductItem.id.label('product_item_id'),
            ProductItem.original_product_item_id.label('original_product_item_id'),
            ProductItem.name.label('product_item_name'),
            OrderedProductItemToken.id.label('token_id'),
            Seat.id.label('seat_id'),
            Seat.name.label('seat_name'),
            SalesSegmentGroup.id.label('sales_segment_group_id'),
            SalesSegmentGroup.name.label('sales_segment_group_name'),
            DeliveryMethod.delivery_plugin_id
        ) \
            .join(Organization, Organization.id == Order.organization_id) \
            .join(OrganizationSetting, OrganizationSetting.organization_id == Organization.id) \
            .join(Performance, Performance.id == Order.performance_id) \
            .join(Event, Event.id == Performance.event_id) \
            .join(EventSetting, EventSetting.event_id == Event.id) \
            .join(PaymentDeliveryMethodPair, PaymentDeliveryMethodPair.id == Order.payment_delivery_method_pair_id) \
            .join(DeliveryMethod, DeliveryMethod.id == PaymentDeliveryMethodPair.delivery_method_id) \
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
            .filter(DeliveryMethod.delivery_plugin_id.in_([SEJ_DELIVERY_PLUGIN_ID, SKIDATA_QR_DELIVERY_PLUGIN_ID])) \
            .filter(SkidataBarcode.canceled_at.is_(None)).filter(SkidataBarcode.sent_at.is_(None)) \
            .filter(Order.canceled_at.is_(None)).filter(Order.refunded_at.is_(None)).filter(Order.paid_at.isnot(None))

        offset_day = args.offset
        days_delta = args.days_delta
        now_datetime = datetime.now()
        start_datetime = _get_target_datetime(now_datetime, offset_day)
        end_datetime = _get_target_datetime(now_datetime, offset_day + days_delta)

        orders = query.filter(Performance.open_on.between(start_datetime, end_datetime)).all()
        logger.info('day:start_datetime={},one_below_datetime={}'.format(start_datetime, end_datetime))

        # TODO for test search. Will be removed.
        orders = query.all()
        print(len(orders))

        all_data = []
        ssg_prop_dict = dict()
        pi_prop_dict = dict()

        for order in orders:
            # skidata plugin idの場合
            if order.delivery_plugin_id == SKIDATA_QR_DELIVERY_PLUGIN_ID:
                seat_gate_name = _get_gate_name(session, order.seat_id)
                ssg_prop_value = _get_data_property_value(ssg_prop_dict, session, order.organization_id,
                                                          order.sales_segment_group_id,
                                                          SkidataPropertyTypeEnum.SalesSegmentGroup.v)
                # 抽選からオーダーを作ると、original_product_item_idになりました。
                product_item_id = order.original_product_item_id if order.original_product_item_id \
                    else order.product_item_id
                pi_prop_value = _get_data_property_value(pi_prop_dict, session, order.organization_id,
                                                         product_item_id,
                                                         SkidataPropertyTypeEnum.ProductItem.v)
                order_data = _create_data_by_order(order, seat_gate_name, ssg_prop_value, pi_prop_value)
                all_data.extend(order_data)
            elif order.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
                # TODO create sej data.
                pass
            else:
                pass

        # send data with group.
        split_data = [all_data[i:i + SKIDATA_SPLIT_COUNT]
                      for i in range(0, len(all_data), SKIDATA_SPLIT_COUNT)]
        for data_objs in split_data:
            print('pattern 1: sent data: ', len(data_objs))
            # タスクステータス更新
            transaction.begin()
            try:
                barcode_objs = []
                qr_objs = []
                for data_obj in data_objs:
                    barcode_objs.append(data_obj['barcode_obj'])
                    qr_objs.append(data_obj['qr_obj'])
                _prepare_barcode_data(barcode_objs, now_datetime)
                _send_qr_objs_to_hsh(qr_objs)
                transaction.abort()  # TODO for test, Will be replaced with transaction.commit().
            except Exception as e:
                transaction.abort()
                logger.error('e: ' + e.message)

        # TODO for test
        print('pattern 1:', (current_milli_time() - start_time),
              'millisecond for', str(len(all_data)), 'count within', str(len(orders)), 'orders')
    except Exception as e:
        logger.error('e: '+e.message)
        # TODO for debug log. we will remove this log at last.
        import traceback
        traceback.print_exc()

    conn.close()
    logger.info('send_white_list_data_to_skidata: end batch')


def _create_data_by_order(order, seat_gate_name, ssg_prop_value, pi_prop_value):
    order_data = []
    barcode_obj = SkidataBarcode.find_by_token_id(order.token_id, DBSession())
    qr_obj = dict(
        data=barcode_obj.data,
        order_no=order.order_no,
        open_on=order.open_on,
        start_on=order.start_on,
        stock_type_name=order.stock_type_name,
        product_name=order.product_name,
        product_item_name=order.product_item_name,
        gate=seat_gate_name,
        seat_name=order.seat_name if order.seat_name else '',
        sales_segment_group_name=order.sales_segment_group_name,
        ssg_property_value=ssg_prop_value,
        pi_property_value=pi_prop_value,
    )
    data_obj = dict(
        barcode_obj=barcode_obj,
        qr_obj=qr_obj
        )
    order_data.append(data_obj)
    return order_data


def _prepare_barcode_data(barcode_objs, now_datetime):
    for barcode in barcode_objs:
        barcode.sent_at = now_datetime
        barcode.save()


def _send_qr_objs_to_hsh(qr_objs):
    # TODO Send qr_obj to HSH service.
    # print(qr_objs)
    pass
