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
    Product, ProductItem, Stock, StockType, Seat,
    PaymentDeliveryMethodPair, DeliveryMethod)
from altair.app.ticketing.skidata.models import SkidataBarcode
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID, SKIDATA_QR_DELIVERY_PLUGIN_ID

logger = logging.getLogger(__name__)

# 多重起動防止
LOCK_TIMEOUT = 10

# 1000件としているのはSKIDATAが推奨する一回のリクエスト量です。
LOCK_NAME = __name__
SKIDATA_SPLIT_COUNT = 1000


def _get_stock_type_by_id(session, stock_type_id):
    return session.query(StockType).filter(StockType.id == stock_type_id).one()


def _get_target_datetime(days):
    """
    If now time is 2019-11-07 10:22:25 and we input days as 1,
    we will get 2019-11-08 00:00:00 as result.
    :param days: plus days.
    :return:  example: 2019-11-08 00:00:00
    """
    now_datetime = datetime.now()
    if days == 0:
        return now_datetime
    dt = now_datetime + timedelta(days=days)
    dt = dt.replace(minute=0, hour=0, second=0, microsecond=0)
    return dt


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
        # 2,Order->Performance->Event->EventSetting->EventSetting.enable_skidata = 1 & Performance.public = 1
        # 3,Order->PaymentDeliveryMethodPair->DeliveryMethod->
        #   DeliveryMethod.delivery_plugin_id in [SEJ_DELIVERY_PLUGIN_ID, SKIDATA_QR_DELIVERY_PLUGIN_ID]
        # 4,Order->OrderedProduct->Product->Product.name
        # 5,Order->OrderedProduct->OrderedProductItem->ProductItem->ProductItem.name
        # 6,Order->OrderedProduct->OrderedProductItem->OrderedProductItemToken->
        #   SkidataBarcode.data & [SkidataBarcode sent_at is NULL and canceled_at is NULL]
        # 7,Order->OrderedProduct->OrderedProductItem->OrderedProductItemToken->SkidataBarcode->Seat.name
        # 8,Order->OrderedProduct->OrderedProductItem->ProductItem->OrderedProductItemToken->Seat->Stock->StockType.name
        # 9,Order->[Order canceled_at is NULL and refunded_at is NULL and paid_at is not NULL]

        query = session.query(Order) \
            .join(Organization).join(OrganizationSetting) \
            .join(Performance).join(Event).join(EventSetting) \
            .join(PaymentDeliveryMethodPair).join(DeliveryMethod) \
            .join(OrderedProduct).join(Product)\
            .join(OrderedProductItem).join(ProductItem).join(OrderedProductItemToken) \
            .outerjoin(Seat, Seat.id == OrderedProductItemToken.seat_id) \
            .join(Stock, Stock.id == ProductItem.stock_id).join(StockType) \
            .join(SkidataBarcode) \
            .filter(OrganizationSetting.enable_skidata == 1) \
            .filter(EventSetting.enable_skidata == 1).filter(Performance.public == 1) \
            .filter(DeliveryMethod.delivery_plugin_id.in_([SEJ_DELIVERY_PLUGIN_ID, SKIDATA_QR_DELIVERY_PLUGIN_ID])) \
            .filter(SkidataBarcode.canceled_at.is_(None)).filter(SkidataBarcode.sent_at.is_(None)) \
            .filter(Order.canceled_at.is_(None)).filter(Order.refunded_at.is_(None)).filter(Order.paid_at.isnot(None))

        offset_day = args.offset
        days_delta = args.days_delta
        start_datetime = _get_target_datetime(offset_day)
        end_datetime = _get_target_datetime(offset_day + days_delta)
        now_datetime = datetime.now()

        orders = query.filter(Performance.open_on.between(start_datetime, end_datetime)).all()
        logger.info('day:start_datetime={},one_below_datetime={}'.format(start_datetime, end_datetime))

        # TODO for test search. Will be removed.
        orders = query.all()

        all_skidatas = []
        for order in orders:
            # skidata plugin idの場合
            if order.delivery_plugin_id == SKIDATA_QR_DELIVERY_PLUGIN_ID:
                order_skidatas = _create_skidatas_by_order(session, order)
                all_skidatas.extend(order_skidatas)
            elif order.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
                # TODO create sej data.
                pass
            else:
                pass

        split_skidatas = [all_skidatas[i:i + SKIDATA_SPLIT_COUNT]
                          for i in range(0, len(all_skidatas), SKIDATA_SPLIT_COUNT)]
        for skidatas in split_skidatas:
            print('pattern 2: sent data: ', len(skidatas))
            # タスクステータス更新
            transaction.begin()
            try:
                qr_obj_data = None
                for skidata in skidatas:
                    _prepare_skidata_barcode_data(skidata['skidata_barcode'], now_datetime)
                    qr_obj = skidata['qr_obj']
                    # TODO create json or xml with qr_obj.
                    # print(qr_obj)
                _send_qr_obj_data_to_hsh(qr_obj_data)
                transaction.abort()  # TODO for test, Will be replaced with transaction.commit().
            except Exception as e:
                transaction.abort()
                logger.error('e: ' + e.message)

        # TODO for test
        print('pattern 2:', (current_milli_time() - start_time),
              'millisecond for', str(len(all_skidatas)), 'count with', str(len(orders)), 'orders')
    except Exception as e:
        logger.error('e: '+e.message)

    conn.close()
    logger.info('send_white_list_data_to_skidata: end batch')


def _create_skidatas_by_order(session, order):
    order_skidatas = []
    for order_product in order.ordered_products:
        product = order_product.product
        sales_segment_group = product.sales_segment.sales_segment_group
        ssg_opi_sp_value = sales_segment_group.skidata_property.value
        performance = order.performance
        for ordered_product_item in order_product.ordered_product_items:
            product_item = ordered_product_item.product_item
            opi_sp_value = product_item.skidata_property.value
            stock_type = _get_stock_type_by_id(session, product_item.stock.stock_type_id)
            for token in ordered_product_item.tokens:
                seat = token.seat
                skidata_barcode = SkidataBarcode.find_by_token_id(token.id, DBSession())
                qr_obj = dict(
                    data=skidata_barcode.data,
                    order_no=order.order_no,
                    open_on=performance.open_on,
                    start_on=performance.start_on,
                    stock_type_name=stock_type.name,
                    product_name=product.name,
                    product_item_name=product_item.name,
                    gate=seat.__getitem__('gate') if seat else '',
                    seat_name=seat.name if seat else '',
                    sales_segment_group_name=sales_segment_group.name,
                    ssg_opi_sp_value=ssg_opi_sp_value,
                    opi_sp_value=opi_sp_value,
                )
                skidata = dict(
                    skidata_barcode=skidata_barcode,
                    qr_obj=qr_obj
                )
                order_skidatas.append(skidata)
    return order_skidatas


def _prepare_skidata_barcode_data(skidata_barcode, now_datetime):
    skidata_barcode.sent_at = now_datetime
    skidata_barcode.save()


def _send_qr_obj_data_to_hsh(qr_obj_data):
    # TODO Send qr_obj to HSH service.
    pass
