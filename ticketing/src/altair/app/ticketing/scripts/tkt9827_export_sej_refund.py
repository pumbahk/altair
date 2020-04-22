#! /usr/bin/env python
#-*- coding: utf-8 -*-

import argparse
import logging
import csv
from datetime import datetime

from pyramid.paster import bootstrap

from altair.app.ticketing.core.models import Performance, StockType, ProductItem, Product, Stock, SalesSegmentGroup, \
    Seat, SalesSegment
from altair.app.ticketing.orders.models import Order, OrderedProductItemToken
from altair.app.ticketing.sej.models import SejRefundTicket, SejTicket
from altair.sqlahelper import get_db_session

logger = logging.getLogger(__name__)

"""
SEJ払戻しステータスデータ抽出用のスクリプト
"""

csv_header = [
    ('order_no', u'予約番号'),
    ('stock_type_name', u'席種'),
    ('product_name', u'商品名'),
    ('product_item_name', u'商品明細名'),
    ('seat_name', u'席名称'),
    ('sent_at', u'データ送信日時'),
    ('refunded_at', u'コンビニ払戻日時'),
    ('barcode_number', u'バーコード番号'),
    ('refund_ticket_amount', u'払戻金額(チケット分)'),
    ('refund_other_amount', u'払戻金額(手数料分)'),
    ('status', u'払戻状態'),
    ('performance_name', u'パフォーマンス名'),
    ('performance_start_on', u'公演日時'),
    ('sales_segment_group_name', u'販売区分')
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-eid', '--event_id', metavar='event_id', type=str, required=True)
    parser.add_argument('-pid', '--performance_id', metavar='performance_id', type=str, required=False)

    args = parser.parse_args()
    env = bootstrap(args.config)
    request = env['request']

    slave_session = get_db_session(request, name="slave")
    query = slave_session.query(
        SejRefundTicket.order_no.label('order_no'),
        StockType.name.label('stock_type_name'),
        Product.name.label('product_name'),
        ProductItem.name.label('product_item_name'),
        Seat.name.label('seat_name'),
        SejRefundTicket.sent_at.label('sent_at'),
        SejRefundTicket.refunded_at.label('refunded_at'),
        SejRefundTicket.ticket_barcode_number.label('barcode_number'),
        SejRefundTicket.refund_ticket_amount.label('refund_ticket_amount'),
        SejRefundTicket.refund_other_amount.label('refund_other_amount'),
        SejRefundTicket.status.label('status'),
        Performance.name.label('performance_name'),
        Performance.start_on.label('performance_start_on'),
        SalesSegmentGroup.name.label('sales_segment_group_name')
    ).join(
        Order, SejRefundTicket.order_no == Order.order_no
    ).join(
        SejTicket, SejTicket.barcode_number == SejRefundTicket.ticket_barcode_number
    ).join(
        ProductItem,
        Product,
        Stock,
        StockType,
    ).join(
        OrderedProductItemToken, OrderedProductItemToken.id == SejTicket.ordered_product_item_token_id
    ).outerjoin(
        Seat, Seat.id == OrderedProductItemToken.seat_id
    ).join(
        SalesSegment, SalesSegment.id == Order.sales_segment_id
    ).join(
        SalesSegmentGroup, SalesSegmentGroup.id == SalesSegment.sales_segment_group_id
    ).join(
        Performance, Performance.id == Order.performance_id
    ).filter(
        Performance.event_id == args.event_id
    )

    if args.performance_id:
        query = query.filter(Performance.id == args.performance_id)

    all_data = query.all()
    logger.info(u'{} query_data were found.'.format(len(all_data)))

    export_data = []
    for refund_data in all_data:
        obj = dict(
            order_no=refund_data.order_no,
            stock_type_name=refund_data.stock_type_name.encode('shift-jis'),
            product_name=refund_data.product_name.encode('shift-jis'),
            product_item_name=refund_data.product_item_name.encode('shift-jis'),
            seat_name=refund_data.seat_name.encode('shift-jis'),
            sent_at=refund_data.sent_at,
            refunded_at=refund_data.refunded_at,
            barcode_number=refund_data.barcode_number,
            refund_ticket_amount=refund_data.refund_ticket_amount,
            refund_other_amount=refund_data.refund_other_amount,
            status=refund_data.status,
            performance_name=refund_data.performance_name.encode('shift-jis'),
            performance_start_on=refund_data.performance_start_on,
            sales_segment_group_name=refund_data.sales_segment_group_name.encode('shift-jis'),
        )
        export_data.append(obj)

    logger.info(u'{} export_data were found.'.format(len(export_data)))
    logger.info(u'start exporting csv...')
    try:
        # export_dataをcsvとして書き出す
        filename = 'eid_{}_export_sej_refund_csv_{:%Y%m%d-%H%M%S}.csv'.format(args.event_id, datetime.now())
        if args.performance_id:
            filename = 'eid_{}_pid_{}_export_sej_refund_csv_{:%Y%m%d-%H%M%S}.csv'.format(
                str(args.event_id), str(args.performance_id), datetime.now())
        f = open(filename, 'w')
        csvWriter = csv.writer(f)
        # csv_header書き出し
        keys = [k for k, v in csv_header]
        columns = [v.encode('shift-jis') for k, v in csv_header]
        csvWriter.writerow(columns)
        # body書き出し(headerと合うように順番を気にする)
        for d in export_data:
            row = []
            for k in keys:
                row.append(d[k])
            csvWriter.writerow(row)
        logger.info(u'The filename is {}'.format(filename))
    except Exception as e:
        logger.error(e)
    finally:
        f.close()
    logger.info(u'end exporting csv...')


if __name__ == '__main__':
    main()
