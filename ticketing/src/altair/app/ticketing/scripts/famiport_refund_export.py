#! /usr/bin/env python
#-*- coding: utf-8 -*-

import argparse
import logging
import csv
from datetime import datetime

from sqlalchemy.sql.expression import case

from pyramid.paster import bootstrap, setup_logging
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.core.models import Performance, StockType, ProductItem, Product, SalesSegmentGroup, \
    Seat, SalesSegment,Event
from altair.app.ticketing.orders.models import Order, OrderedProductItemToken,OrderedProduct,OrderedProductItem
from altair.sqlahelper import get_db_session

from altair.app.ticketing.famiport.models import FamiPortOrder, FamiPortTicket, FamiPortRefundEntry, FamiPortRefund, \
    FamiPortPerformance
from altair.app.ticketing.famiport.userside_models import AltairFamiPortPerformance

logger = logging.getLogger(__name__)

"""
fmaiport払戻しステータスデータ抽出用のスクリプト
"""

csv_header = [
    ('order_no', u'予約番号'),
    ('report_generated_at', u'データ送信日時'),
    ('refunded_at', u'コンビニ払戻日時'),
    ('barcode_number', u'バーコード番号'),
    ('ticket_payment', u'払戻金額(チケット分)'),
    ('other_fees', u'払戻金額(手数料分)'),
    ('refund_status', u'払戻状態'),
    ('stock_type_name', u'席種'),
    ('product_name', u'商品名'),
    ('product_item_name', u'商品明細名'),
    ('seat_name', u'席名称'),
    ('performance_name', u'パフォーマンス名'),
    ('performance_start_on', u'公演日時'),
    ('sales_segment_group_name', u'販売区分')
]

# -eid：イベントID　必須
# -pid：パフォーマンスID
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-eid', '--event_id', metavar='event_id', type=str, required=True)
    parser.add_argument('-pid', '--performance_id', metavar='performance_id', type=str, required=False)

    args = parser.parse_args()
    env = bootstrap(args.config)
    request = env['request']

    setup_logging(args.config)

    try:
        famiport_db_session = get_db_session(request, name='famiport_slave')
        altair_slave_session = get_db_session(request, name="slave")
    except Exception as e:
        logger.warning(u'Failed to get db session.(famiport_refund_export): {}'.format(e))
        raise

    refund_id_data = get_refund_id_by_eid_pid(altair_slave_session, args)
    if len(refund_id_data) > 0:
        if args.performance_id:
            famiport_performance_ids = get_famiport_performance_id(famiport_db_session, altair_slave_session,
                                                                   refund_id_data, args.performance_id)
            fami_refund_ids = get_famiport_refund_ids_for_performance(famiport_db_session, refund_id_data,
                                                                      famiport_performance_ids)
            famiport_export_data = famiport_export(famiport_db_session, fami_refund_ids, famiport_performance_ids)
            altair_export_data = altair_export(altair_slave_session, args, fami_refund_ids)
            write_csv(args, altair_export_data, famiport_export_data, csv_header)
        else:
            famiport_refund_ids = get_famiport_refund_ids_for_event(famiport_db_session, refund_id_data)
            if len(famiport_refund_ids) > 0:
                famiport_export_data = famiport_export(famiport_db_session, famiport_refund_ids)
                altair_export_data = altair_export(altair_slave_session, args, famiport_refund_ids)
                write_csv(args, altair_export_data, famiport_export_data, csv_header)
            else:
                print("refund_id does not exist on famiport side by event id", args.event_id)
    else:
        print("No refund information or incorrect event_id or performance_id", args.event_id, args.performance_id)


# famiportデータを取得する
# famiport_db_session:famiport DB session
# fami_refund_ids:famiport側のrefund_id
# fami_pf_ids:famiport performance id
def famiport_export(famiport_db_session, fami_refund_ids, fami_pf_ids=None):
    queryfami = famiport_db_session.query(
        FamiPortOrder.order_no.label('order_no'),
        FamiPortRefundEntry.report_generated_at.label('report_generated_at'),
        FamiPortRefundEntry.refunded_at.label('refunded_at'),
        FamiPortTicket.barcode_number.label('barcode_number'),
        FamiPortRefundEntry.ticket_payment.label('ticket_payment'),
        FamiPortRefundEntry.other_fees.label('other_fees'),
        case([(FamiPortRefundEntry.refunded_at != None, "1")], else_="").label("refund_status")
    ).join(
        FamiPortTicket, FamiPortTicket.famiport_order_id == FamiPortOrder.id
    ).join(
        FamiPortRefundEntry, FamiPortRefundEntry.famiport_ticket_id == FamiPortTicket.id
    ).join(
        FamiPortRefund, FamiPortRefund.id == FamiPortRefundEntry.famiport_refund_id
    ) .join(
        FamiPortPerformance, FamiPortPerformance.id == FamiPortOrder.famiport_performance_id
    ).filter(
        FamiPortRefund.userside_id.in_(fami_refund_ids)
    )
    if fami_pf_ids:
        queryfami.filter(
            FamiPortPerformance.id.in_(fami_pf_ids)
        )

    queryfami.order_by(FamiPortOrder.order_no)

    fami_data = queryfami.all()
    famiport_export_data = []
    for fami_refund_data in fami_data:
        famiobj = dict(
            order_no=fami_refund_data.order_no,
            report_generated_at=fami_refund_data.report_generated_at,
            refunded_at=fami_refund_data.refunded_at,
            barcode_number=fami_refund_data.barcode_number,
            ticket_payment=fami_refund_data.ticket_payment,
            other_fees=fami_refund_data.other_fees,
            refund_status=fami_refund_data.refund_status,
        )
        famiport_export_data.append(famiobj)
    return famiport_export_data


# altairデータを取得する
# altair_db_session:altair DB session
# args: パラメータ（eid,pid）
# fami_refund_ids:famiport側のrefund_id
def altair_export(altair_db_session, args, fami_refund_ids):
    query_altair = altair_db_session.query(
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
        ProductItem, ProductItem.product_id == Product.id
    ).join(
        StockType, StockType.id == Product.seat_stock_type_id
    ).join(
        SalesSegment, SalesSegment.id == Order.sales_segment_id
    ).join(
        SalesSegmentGroup, SalesSegmentGroup.id == SalesSegment.sales_segment_group_id
    ).filter(
        Performance.event_id == args.event_id
    ).filter(
        Order.refund_id.in_(fami_refund_ids)
    )

    if args.performance_id:
        query_altair = query_altair.filter(Performance.id == args.performance_id)

    query_altair.order_by(Order.order_no)

    all_data = query_altair.all()
    logger.info(u'{} query_data were found.'.format(len(all_data)))

    altair_export_data = []
    for refund_data in all_data:
        obj = dict(
            order_no=refund_data.order_no,
            stock_type_name=refund_data.stock_type_name.encode('shift-jis'),
            product_name=refund_data.product_name.encode('shift-jis'),
            product_item_name=refund_data.product_item_name.encode('shift-jis'),
            seat_name=refund_data.seat_name.encode('shift-jis') if refund_data.seat_name else '',
            performance_name=refund_data.performance_name.encode('shift-jis'),
            performance_start_on=refund_data.performance_start_on,
            sales_segment_group_name=refund_data.sales_segment_group_name.encode('shift-jis'),
        )
        altair_export_data.append(obj)

    return altair_export_data


# csvファイルに書き込む
# args:パラメータ（eid,pid）
# altair_export_data:altair側で検索したデータ
# famiport_export_data:famiport側で検索したデータ
# csv_header:項目名
def write_csv(args, altair_export_data, famiport_export_data, csv_header):
    all_data = []
    for (fami_d, altair_d) in zip(famiport_export_data, altair_export_data):
        obj = dict(
            order_no=fami_d['order_no'],
            report_generated_at=fami_d['report_generated_at'],
            refunded_at=fami_d['refunded_at'],
            barcode_number=fami_d['barcode_number'],
            ticket_payment=fami_d['ticket_payment'],
            other_fees=fami_d['other_fees'],
            refund_status=fami_d['refund_status'],
            stock_type_name=altair_d['stock_type_name'],
            product_name=altair_d['product_name'],
            product_item_name=altair_d['product_item_name'],
            seat_name=altair_d['seat_name'] if altair_d['seat_name'] else '',
            performance_name=altair_d['performance_name'],
            performance_start_on=altair_d['performance_start_on'],
            sales_segment_group_name=altair_d['sales_segment_group_name']
        )
        all_data.append(obj)

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


# argsより Orderからrefund_idを取得する
# altair_db_session:altair DB session
# args: パラメータ（eid,pid）
def get_refund_id_by_eid_pid(altair_db_session, args):
    query_refund_id = altair_db_session.query(
        Order
    ).distinct(
        Order.refund_id
    ).join(
        Performance, Performance.id == Order.performance_id
    ).join(
        Event, Event.id == Performance.event_id
    ).filter(
        Performance.event_id == args.event_id
    ).filter(
        Order.refund_id.isnot(None)
    )

    if args.performance_id:
        query_refund_id = query_refund_id.filter(Performance.id == args.performance_id)

    refund_ids = query_refund_id.all()
    rf_ids = []
    for refund_id in refund_ids:
        rf_ids.append(refund_id.refund_id)

    return rf_ids


# event idを指定する場合、famiport refund_idを取得する
# famiport_db_session: famiport DB session
# refund_ids:altairで取得したrefund_id
def get_famiport_refund_ids_for_event(famiport_db_session, refund_ids):
    query = famiport_db_session.query(
        FamiPortRefund.userside_id,
        FamiPortOrder.famiport_performance_id,
        FamiPortOrder.order_no
    ).join(
        FamiPortRefundEntry, FamiPortRefundEntry.famiport_refund_id == FamiPortRefund.id
    ).join(
        FamiPortTicket, FamiPortTicket.id == FamiPortRefundEntry.famiport_ticket_id
    ).join(
        FamiPortOrder, FamiPortOrder.id == FamiPortTicket.famiport_order_id
    ).join(
        FamiPortPerformance, FamiPortPerformance.id == FamiPortOrder.famiport_performance_id
    ).filter(
        FamiPortRefund.userside_id.in_(refund_ids)
    ).group_by(
        FamiPortRefund.userside_id
    )

    refund_ids = query.all()
    fami_refund_ids = []
    for rid in refund_ids:
        fami_refund_ids.append(rid.userside_id)
    return fami_refund_ids


# performance idを指定する場合、famiport refund_idを取得する
# famiport_db_session: famiport DB session
# refund_ids: altairで取得したrefund_id
# fami_pf_ids: famipor performance id
def get_famiport_refund_ids_for_performance(famiport_db_session, refund_ids, fami_pf_ids):
    query = famiport_db_session.query(
        FamiPortRefund.userside_id
    ).join(
        FamiPortRefundEntry, FamiPortRefundEntry.famiport_refund_id == FamiPortRefund.id
    ).join(
        FamiPortTicket, FamiPortTicket.id == FamiPortRefundEntry.famiport_ticket_id
    ).join(
        FamiPortOrder, FamiPortOrder.id == FamiPortTicket.famiport_order_id
    ).join(
        FamiPortPerformance, FamiPortPerformance.id == FamiPortOrder.famiport_performance_id
    ).filter(
        FamiPortRefund.userside_id.in_(refund_ids)
    ) .filter(
        FamiPortPerformance.id.in_(fami_pf_ids)
    ).group_by(
        FamiPortRefund.userside_id
    )

    refund_ids = query.all()
    fami_refund_ids = []
    for rid in refund_ids:
        fami_refund_ids.append(rid.userside_id)
    return fami_refund_ids


# FamiPortPerformanceよりfamiport_performance_idを取得する
# famiport_db_session: famiport DB session
# altair_db_session: altair DB session
# refund_ids:altairで取得したrefund_id
# altair_performance_id:パラメータで指定したパフォーマンスID
def get_famiport_performance_id(famiport_db_session, altair_db_session, refund_ids, altair_performance_id):
    fami_query = famiport_db_session.query(
        FamiPortOrder.famiport_performance_id,
        FamiPortPerformance.userside_id
    ).join(
        FamiPortTicket, FamiPortTicket.famiport_order_id == FamiPortOrder.id
    ).join(
        FamiPortRefundEntry, FamiPortRefundEntry.famiport_ticket_id == FamiPortTicket.id
    ).join(
        FamiPortRefund, FamiPortRefund.id == FamiPortRefundEntry.famiport_refund_id
    ) .join(
        FamiPortPerformance, FamiPortPerformance.id == FamiPortOrder.famiport_performance_id
    ).filter(
        FamiPortRefund.userside_id.in_(refund_ids)
    ).group_by(
        FamiPortOrder.famiport_performance_id
    )

    res = fami_query.all()

    famiport_performance_userside_ids = []
    for pf_id in res:
        obj = dict(
            famiport_performance_id=pf_id.famiport_performance_id,
            userside_id=pf_id.userside_id,
        )
        famiport_performance_userside_ids.append(obj)

    link_id = get_altair_famiport_link_id(altair_db_session, famiport_performance_userside_ids,
                                          altair_performance_id)

    famiport_pf_ids = []
    for obj in famiport_performance_userside_ids:
        if obj['userside_id'] == link_id:
            famiport_pf_ids.append(obj['famiport_performance_id'])

    return famiport_pf_ids


# performanceidにより AltairFamiPortPerformanceから連携IDを取得する。
# altair_db_session: altair db session
# afpids: famiport performance userside id
# altair_pf_id: altair performance id
def get_altair_famiport_link_id(altair_db_session, famiport_performance_userdide_ids, altair_pf_id):
    userside_ids = []
    for fpui in famiport_performance_userdide_ids:
        userside_ids.append(fpui['userside_id'])

    query = altair_db_session.query(
        AltairFamiPortPerformance.id
    ).filter(
        AltairFamiPortPerformance.id.in_(userside_ids)
    ).filter(
        AltairFamiPortPerformance.performance_id == altair_pf_id
    )

    res = query.first()
    return res.id


if __name__ == '__main__':
    main()
