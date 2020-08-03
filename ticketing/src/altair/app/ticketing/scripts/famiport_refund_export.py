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
        famiport_info = get_famiport_info(request, refund_order_info)
        write_csv(args, refund_order_info, famiport_info, csv_header)
    else:
        print("No refund information or incorrect event_id or performance_id", args.event_id, args.performance_id)
    logger.info("famiport refund data extraction ends(famiport_refund_export.py)")

# csvファイルに書き込む
# args:パラメータ（eid,pid）
# altair_export_data:altair側で検索したデータ
# famiport_export_data:famiport側で検索したデータ
# csv_header:項目名
def write_csv(args, altair_refund_info, famiport_info, csv_header):
    all_data = []
    for (fm_info, altair_info) in zip(famiport_info, altair_refund_info):
        obj = dict(
            order_no=fm_info['order_no'],
            stock_type_name=altair_info.stock_type_name.encode('shift-jis'),
            product_name=altair_info.product_name.encode('shift-jis'),
            product_item_name=altair_info.product_item_name.encode('shift-jis'),
            seat_name=altair_info.seat_name.encode('shift-jis') if altair_info.seat_name else '',
            report_generated_at=fm_info['report_generated_at'],
            refunded_at=fm_info['refunded_at'],
            barcode_number='{0}{1}'.format('1', fm_info['barcode_number']),
            ticket_payment=fm_info['ticket_payment'],
            other_fees=fm_info['other_fees'],
            refund_status=fm_info['refund_status'],
            performance_name=altair_info.performance_name.encode('shift-jis'),
            performance_start_on=altair_info.performance_start_on,
            sales_segment_group_name=altair_info.sales_segment_group_name.encode('shift-jis')
        )
        all_data.append(obj)
    print(u'start exporting csv...')
    try:
        # export_dataをcsvとして書き出す
        filename = 'eid_{}_export_refund_csv_{:%Y%m%d-%H%M%S}.csv'.format(args.event_id, datetime.now())
        print(filename)
        if args.performance_id:
            filename = 'eid_{}_pid_{}_export_refund_csv_{:%Y%m%d-%H%M%S}.csv'.format(
                str(args.event_id), str(args.performance_id), datetime.now())
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
        SalesSegmentGroup.name.label('sales_segment_group_name')
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
# request: famiport refund dataを取得するため
# refund_order_info: altair側で取得した払戻情報
# return export_data:出力データ
def get_famiport_info(request, refund_order_info):
    famiport_info = []
    print("******** refund info count")
    print("refund_order_info count = %d" % len(refund_order_info))
    print("******** refund info count")

    last_order_no = ''
    for order_info in refund_order_info:
        order_no = order_info.order_no
        query = search_refund_ticket_by_order_no(request, order_no)
        count = query.count()
        famiport_refund_info = query.all()

        if famiport_refund_info is None or count == 0 or last_order_no == order_no:
            continue

        last_order_no = order_no
        for fm_refund_info in famiport_refund_info:
            refund_status = ''
            if fm_refund_info.refunded_at:
                refund_status = '1'

            export_info = dict(
                order_no=fm_refund_info.famiport_ticket.famiport_order.order_no,
                report_generated_at=fm_refund_info.report_generated_at,
                refunded_at=fm_refund_info.refunded_at,
                barcode_number=fm_refund_info.famiport_ticket.barcode_number,
                ticket_payment=fm_refund_info.ticket_payment,
                other_fees=fm_refund_info.other_fees,
                refund_status=refund_status,
            )
            famiport_info.append(export_info)

    return famiport_info


if __name__ == '__main__':
    main()
