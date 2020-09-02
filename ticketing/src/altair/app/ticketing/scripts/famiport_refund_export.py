#! /usr/bin/env python
#-*- coding: utf-8 -*-

import argparse
import logging
import csv
from datetime import datetime
from pyramid.paster import bootstrap, setup_logging
from altair.app.ticketing.core.models import Performance, StockType, ProductItem, Product, SalesSegmentGroup, \
    Seat, SalesSegment, Event, PaymentDeliveryMethodPair, DeliveryMethod, DeliveryMethodPlugin
from altair.app.ticketing.payments.plugins import FAMIPORT_DELIVERY_PLUGIN_ID
from altair.app.ticketing.orders.models import Order, OrderedProductItemToken,OrderedProduct,OrderedProductItem
from altair.sqlahelper import get_db_session
from altair.app.ticketing.famiport.optool.api import search_refund_ticket_by_order_no
logger = logging.getLogger(__name__)

"""
fmaiport払戻しステータスデータ抽出用のスクリプト
"""

csv_header = [
    ('order_no', u'予約番号'),
    ('stock_type_name', u'席種'),
    ('product_name', u'商品名'),
    ('product_item_name', u'商品明細名'),
    ('seat_name', u'席名称'),
    ('report_generated_at', u'データ送信日時'),
    ('refunded_at', u'コンビニ払戻日時'),
    ('barcode_number', u'バーコード番号'),
    ('ticket_payment', u'払戻金額(チケット分)'),
    ('other_fees', u'払戻金額(手数料分)'),
    ('refund_status', u'払戻状態'),
    ('performance_name', u'パフォーマンス名'),
    ('performance_start_on', u'公演日時'),
    ('sales_segment_group_name', u'販売区分')
]


# -eid：イベントID　必須
# -pid：パフォーマンスID
def main():
    logger.info("famiport refund data extraction starts(famiport_refund_export.py)")
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-eid', '--event_id', metavar='event_id', type=str, required=True)
    parser.add_argument('-pid', '--performance_id', metavar='performance_id', type=str, required=False)

    args = parser.parse_args()
    env = bootstrap(args.config)
    request = env['request']

    setup_logging(args.config)

    try:
        altair_slave_session = get_db_session(request, name="slave")
    except Exception as e:
        logger.warning(u'Failed to get db session.(famiport_refund_export): {}'.format(e))
        raise

    refund_order_info = get_refund_info_by_eid_pid(altair_slave_session, args)

    if len(refund_order_info) > 0:
        export_info = get_export_info(altair_slave_session, request, refund_order_info)
        write_csv(args, export_info, csv_header)
    else:
        print("No refund information or incorrect event_id or performance_id", args.event_id, args.performance_id)
    logger.info("famiport refund data extraction ends(famiport_refund_export.py)")


# csvファイルに書き込む
# args:パラメータ（eid,pid）
# altair_export_data:altair側で検索したデータ
# famiport_export_data:famiport側で検索したデータ
# csv_header:項目名
def write_csv(args, export_info, csv_header):
    print("******** refund info count")
    print("refund_order_info count = %d" % len(export_info))
    print("******** refund info count")
    all_data = []
    for info in export_info:
        obj = dict(
            order_no=info['order_no'],
            stock_type_name=info['stock_type_name'].encode('shift-jis'),
            product_name=info['product_name'].encode('shift-jis'),
            product_item_name=info['product_item_name'].encode('shift-jis'),
            seat_name=info['seat_name'].encode('shift-jis'),
            report_generated_at=info['report_generated_at'],
            refunded_at=info['refunded_at'],
            barcode_number='{0}{1}'.format('1', info['barcode_number']),
            ticket_payment=info['ticket_payment'],
            other_fees=info['other_fees'],
            refund_status=info['refund_status'],
            performance_name=info['performance_name'].encode('shift-jis'),
            performance_start_on=info['performance_start_on'],
            sales_segment_group_name=info['sales_segment_group_name'].encode('shift-jis')
        )
        all_data.append(obj)
    print(u'start exporting csv...')
    try:
        # export_dataをcsvとして書き出す
        filename = 'eid_{}_export_famiport_refund_csv_{:%Y%m%d-%H%M%S}.csv'.format(args.event_id, datetime.now())
        if args.performance_id:
            filename = 'eid_{}_pid_{}_famiport_export_refund_csv_{:%Y%m%d-%H%M%S}.csv'.format(
                str(args.event_id), str(args.performance_id), datetime.now())
        print(filename)
        csv_f = open(filename, 'w')
        csv_writer = csv.writer(csv_f)
        # csv_header書き出し
        keys = [k for k, v in csv_header]
        columns = [v.encode('shift-jis') for k, v in csv_header]
        csv_writer.writerow(columns)

        # body書き出し(headerと合うように順番を気にする)
        for d in all_data:
            row = []
            for k in keys:
                row.append(d[k])
            csv_writer.writerow(row)
        logger.info(u'The filename is {}'.format(filename))
    except Exception as e:
        logger.error(e)
    finally:
        csv_f.close()
    print('end exporting csv...')


# argsより refund 情報を取得する
# altair_db_session:altair DB session
# args: パラメータ（eid,pid）
def get_refund_info_by_eid_pid(altair_db_session, args):
    query = altair_db_session.query(
        Order.order_no.label('order_no'),
        StockType.name.label('stock_type_name'),
        Product.name.label('product_name'),
        ProductItem.name.label('product_item_name'),
        Seat.name.label('seat_name'),
        Performance.name.label('performance_name'),
        Performance.start_on.label('performance_start_on'),
        SalesSegmentGroup.name.label('sales_segment_group_name'),
        Order.refund_id.label('refund_id')
    ).join(
        Performance, Performance.id == Order.performance_id
    ).join(
        Event, Event.id == Performance.event_id
    ).join(
        PaymentDeliveryMethodPair, PaymentDeliveryMethodPair.id == Order.payment_delivery_method_pair_id
    ).join(
        DeliveryMethod, DeliveryMethod.id == PaymentDeliveryMethodPair.delivery_method_id
    ).join(
        DeliveryMethodPlugin, DeliveryMethodPlugin.id == DeliveryMethod.delivery_plugin_id
    ).join(
        OrderedProduct, OrderedProduct.order_id == Order.id
    ).join(
        OrderedProductItem, OrderedProductItem.ordered_product_id == OrderedProduct.id
    ).join(
        OrderedProductItemToken, OrderedProductItemToken.ordered_product_item_id == OrderedProductItem.id
    ).outerjoin(
        Seat, Seat.id == OrderedProductItemToken.seat_id
    ).join(
        Product, Product.id == OrderedProduct.product_id
    ).join(
        ProductItem, ProductItem.id == OrderedProductItem.product_item_id
    ).join(
        StockType, StockType.id == Product.seat_stock_type_id
    ).join(
        SalesSegment, SalesSegment.id == Order.sales_segment_id
    ).join(
        SalesSegmentGroup, SalesSegmentGroup.id == SalesSegment.sales_segment_group_id
    ).filter(Performance.event_id == args.event_id)\
     .filter(Order.canceled_at == None) \
     .filter(Order.deleted_at == None) \
     .filter(Order.refund_id.isnot(None))\
     .filter(DeliveryMethodPlugin.id == FAMIPORT_DELIVERY_PLUGIN_ID)\
     .order_by(Order.order_no)

    if args.performance_id:
        query = query.filter(Performance.id == args.performance_id)

    orders = query.all()
    refund_order_info = []
    for order in orders:
        refund_order_info.append(order)

    return refund_order_info


# famiport refund dataを取得し、出力データを作成する
# altair_slave_session:DB session
# request: famiport refund dataを取得するため
# refund_order_info: altair側で取得した払戻情報
# return export_data:出力データ
def get_export_info(altair_slave_session, request, refund_order_info):
    export_info_list = []

    last_order_no = ''
    for order_info in refund_order_info:
        order_no = order_info.order_no
        refund_id = order_info.refund_id
        query = search_refund_ticket_by_order_no(request, order_no, refund_id)
        count = query.count()
        famiport_refund_info = query.all()

        if famiport_refund_info is None or count == 0 or last_order_no == order_no:
            continue

        last_order_no = order_no
        for fm_refund_info in famiport_refund_info:
            refund_status = ''
            if fm_refund_info.refunded_at:
                refund_status = '1'

            if not fm_refund_info.famiport_ticket.userside_token_id:
                continue

            token_id = fm_refund_info.famiport_ticket.userside_token_id
            token = get_token_by_id(altair_slave_session, token_id)
            ordered_product_item_id = token.ordered_product_item_id
            ordered_product_item = get_ordered_product_item_by_id(altair_slave_session, ordered_product_item_id)

            stock_type = None
            if not token.seat:
                stock_type = ordered_product_item.product_item.stock_type

            if not stock_type:
                stock_type_id = token.seat.stock.stock_type_id
                stock_type = get_stock_type_by_id(altair_slave_session, stock_type_id)

            seat_name = ''
            if token.seat:
                seat_name = token.seat.name

            export_info = dict(
                order_no=fm_refund_info.famiport_ticket.famiport_order.order_no,
                stock_type_name=stock_type.name,
                product_name=ordered_product_item.ordered_product.product.name,
                product_item_name=ordered_product_item.product_item.name,
                seat_name=seat_name,
                report_generated_at=fm_refund_info.report_generated_at,
                refunded_at=fm_refund_info.refunded_at,
                barcode_number=fm_refund_info.famiport_ticket.barcode_number,
                ticket_payment=fm_refund_info.ticket_payment,
                other_fees=fm_refund_info.other_fees,
                refund_status=refund_status,
                performance_name=order_info.performance_name,
                performance_start_on=order_info.performance_start_on,
                sales_segment_group_name=order_info.sales_segment_group_name
            )
            export_info_list.append(export_info)

    return export_info_list


def get_token_by_id(session, token_id):
    return session.query(OrderedProductItemToken) \
        .filter(OrderedProductItemToken.id == token_id) \
        .filter(OrderedProductItemToken.deleted_at == None) \
        .one()


def get_ordered_product_item_by_id(session, ordered_product_item_id):
    return session.query(OrderedProductItem) \
        .filter_by(id=ordered_product_item_id) \
        .filter(OrderedProductItem.deleted_at == None) \
        .one()


def get_stock_type_by_id(session, stock_type_id):
    return session.query(StockType) \
        .filter(StockType.id == stock_type_id) \
        .filter(StockType.deleted_at == None) \
        .one()


if __name__ == '__main__':
    main()
