#! /usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import argparse
import logging
import json
import csv
from sqlalchemy import sql, orm
from sqlalchemy.orm.exc import NoResultFound
from datetime import date, datetime

from pyramid.paster import setup_logging, bootstrap
from altair.app.ticketing.core.models import StockType
from altair.app.ticketing.orders.models import Order, OrderedProductItemToken
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID

logger = logging.getLogger(__name__)

csv_header = [
    ('barcode_no'       , u'バーコード番号'),
    ('order_no'         , u'整理番号'),
    ('branch_no'        , u'チケット枝番'),
    ('last_name'        , u'氏名姓'),
    ('first_name'       , u'氏名名'),
    ('tel'              , u'電話番号'),
    ('performance_date' , u'公演日'),
    ('stock_type'       , u'席種'),
    ('seat_no'          , u'管理番号'),
    ('ticket_count'     , u'チケット枚数'),
    ('gate_name'        , u'ゲート名')
]

def get_stock_type_by_id(session, stock_type_id):
    return session.query(StockType) \
                  .filter(StockType.id == stock_type_id) \
                  .filter(StockType.deleted_at == None) \
                  .one()

def get_token_by_id(session, token_id):
    return session.query(OrderedProductItemToken) \
                  .filter(OrderedProductItemToken.id == token_id) \
                  .filter(OrderedProductItemToken.deleted_at == None) \
                  .one()

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-pid', '--performance_id', metavar='performance_id', type=str, required=True)

    args = parser.parse_args()
    env = bootstrap(args.config)
    request = env['request']
    from sqlahelper import get_session
    session = get_session()

    try:
        if args.performance_id:
            pid = args.performance_id
            orders = session.query(Order) \
                            .filter(Order.performance_id == pid) \
                            .filter(Order.canceled_at == None) \
                            .filter(Order.deleted_at == None) \
                            .all()
            # orderからcsv出力するためのdictへ変換
            export_data = []
            for order in orders:
                # ordersからコンビニ発券なもののみ処理
                # sejの場合
                if order.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
                    sej_order = order.sej_order
                    for i, ticket in enumerate(sej_order.tickets):
                        # Todo:barcode_noの重複チェック
                        try:
                            if not ticket.ordered_product_item_token:
                                logger.warn('SejTicket.barcode_number={} has no relation with token.'.format(ticket.barcode_number))
                                continue
                            if not ticket.ordered_product_item_token.seat:
                                logger.warn('SejTicket.barcode_number={} is not seat selectable.'.format(ticket.barcode_number))
                                continue
                            stock_type_id = ticket.ordered_product_item_token.seat.stock.stock_type_id
                            stock_type = get_stock_type_by_id(session, stock_type_id)
                        except NoResultFound:
                            logger.warn('no result was found for StockType.id={}.(Order.order_no={}, SejTicket.id={})'.format(stock_type_id, order.order_no, sej_order.id))
                            continue

                        retval = dict(
                            barcode_no=ticket.barcode_number,
                            order_no=order.order_no,
                            branch_no=i,
                            last_name=order.shipping_address.last_name.encode('utf-8'),
                            first_name=order.shipping_address.first_name.encode('utf-8'),
                            tel=order.shipping_address.tel_1 or order.shipping_address.tel_2,
                            performance_date=order.performance.start_on,
                            stock_type=stock_type.name.encode('utf-8'),
                            seat_no=ticket.ordered_product_item_token.seat.seat_no,
                            ticket_count=len(sej_order.tickets),
                            gate_name=None
                        )
                        logger.info('barcode_num={}, order_no={}, seat_no={}'.format(retval.get('barcode_no'), retval.get('order_no'), retval.get('seat_no')))
                        export_data.append(retval)
                # famiportの場合
                elif order.delivery_plugin_id == FAMIPORT_DELIVERY_PLUGIN_ID:
                    fm_order = order.famiport_order
                    ticket_likes = fm_order.get('famiport_tickets')
                    for i, ticket_like in enumerate(ticket_likes):
                        try:
                            if not ticket_like.get('userside_token_id'):
                                logger.warn('FamiPortTicket.barcode_number={} has no relation with token.'.format(ticket_like.get('barcode_number')))
                                continue
                            token = get_token_by_id(session, ticket_like.get('userside_token_id'))
                            if not token.seat:
                                logger.warn('FamiPortTicket.barcode_number={} is not seat selectable.'.format(ticket_like.get('barcode_number')))
                                continue
                            stock_type_id = token.seat.stock.stock_type_id
                            stock_type = get_stock_type_by_id(session, stock_type_id)
                        except NoResultFound:
                            logger.warn('no result was found for StockType.id={}.(Order.order_no={}, FamiPortTicket.id={})'.format(stock_type_id, order.order_no, ticket_like.get('id')))
                            continue

                        retval = dict(
                            barcode_no=ticket_like.get('barcode_number'),
                            order_no=order.order_no,
                            branch_no=i,
                            last_name=order.shipping_address.last_name.encode('utf-8'),
                            first_name=order.shipping_address.first_name.encode('utf-8'),
                            tel=order.shipping_address.tel_1 or order.shipping_address.tel_2,
                            performance_date=order.performance.start_on,
                            stock_type=stock_type.name.encode('utf-8'),
                            seat_no=token.seat.seat_no,
                            ticket_count=len(ticket_likes),
                            gate_name=None
                        )
                        logger.info('barcode_num={}, order_no={}, seat_no={}'.format(retval.get('barcode_no'), retval.get('order_no'), retval.get('seat_no')))
                        export_data.append(retval)

            logger.info(u'{} orders was found.'.format(len(orders)))
            logger.info(u'start exporting csv...')
            try:
                # export_dataをcsvとして書き出す
                filename = 'tapirs_csv_{0:%Y%m%d-%H%M%S}.csv'.format(datetime.now())
                f = open(filename, 'w')
                csvWriter = csv.writer(f)
                # csv_header書き出し
                keys = [k for k, v in csv_header]
                columns = [v.encode('utf-8') for k, v in csv_header]
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
    except Exception as e:
        logger.error(e.message)


if __name__ == '__main__':
    main(sys.argv[1:])
