#! /usr/bin/env python
#-*- coding: utf-8 -*-

import argparse
import logging
import csv
from datetime import datetime

from pyramid.paster import bootstrap

from altair.app.ticketing.core.models import Performance, StockType, ProductItem, Product, Stock
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.sej.models import SejRefundTicket, SejTicket
from altair.sqlahelper import get_db_session

logger = logging.getLogger(__name__)

csv_header = [
    ('order_no', u'予約番号'),
    ('stock_type_name', u'席種'),
    ('product_name', u'商品名'),
    ('product_item_name', u'商品明細名'),
    ('sent_at', u'データ送信日時'),
    ('refunded_at', u'コンビニ払戻日時'),
    ('barcode_number', u'バーコード番号'),
    ('refund_ticket_amount', u'払戻金額(チケット分)'),
    ('refund_other_amount', u'払戻金額(手数料分)'),
    ('status', u'払戻状態'),
    ('performance_name', u'パフォーマンス名'),
    ('performance_start_on', u'公演日時')
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-eid', '--event_id', metavar='event_id', type=str, required=True)

    args = parser.parse_args()
    env = bootstrap(args.config)
    request = env['request']

    slave_session = get_db_session(request, name="slave")
    query = slave_session.query(
        SejRefundTicket.order_no.label('order_no'),
        StockType.name.label('stock_type_name'),
        Product.name.label('product_name'),
        ProductItem.name.label('product_item_name'),
        SejRefundTicket.sent_at.label('sent_at'),
        SejRefundTicket.refunded_at.label('refunded_at'),
        SejRefundTicket.ticket_barcode_number.label('barcode_number'),
        SejRefundTicket.refund_ticket_amount.label('refund_ticket_amount'),
        SejRefundTicket.refund_other_amount.label('refund_other_amount'),
        SejRefundTicket.status.label('status'),
        Performance.name.label('performance_name'),
        Performance.start_on.label('performance_start_on'),
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
        Performance, Performance.id == Order.performance_id
    ).filter(
        Performance.event_id == args.event_id
    )

    all_data = query.all()
    logger.info(u'{} query_data were found.'.format(len(all_data)))

    export_data = []
    for refund_data in all_data:
        obj = dict(
            order_no=refund_data.order_no,
            stock_type_name=refund_data.stock_type_name.encode('shift-jis'),
            product_name=refund_data.product_name.encode('shift-jis'),
            product_item_name=refund_data.product_item_name.encode('shift-jis'),
            sent_at=refund_data.sent_at,
            refunded_at=refund_data.refunded_at,
            barcode_number=refund_data.barcode_number,
            refund_ticket_amount=refund_data.refund_ticket_amount,
            refund_other_amount=refund_data.refund_other_amount,
            status=refund_data.status,
            performance_name=refund_data.performance_name.encode('shift-jis'),
            performance_start_on=refund_data.performance_start_on
        )
        export_data.append(obj)

    logger.info(u'{} export_data were found.'.format(len(export_data)))
    logger.info(u'start exporting csv...')
    try:
        # export_dataをcsvとして書き出す
        filename = 'export_sej_refund_csv_{0:%Y%m%d-%H%M%S}.csv'.format(datetime.now())
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
    except Exception as e:
        logger.error(e)
    finally:
        f.close()
    logger.info(u'end exporting csv...')


if __name__ == '__main__':
    main()
