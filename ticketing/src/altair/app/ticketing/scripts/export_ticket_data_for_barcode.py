#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging
import csv
from sqlalchemy.orm.exc import NoResultFound
from sqlahelper import get_session
from datetime import datetime

from pyramid.paster import bootstrap
from altair.app.ticketing.core.models import StockType, ProductItem
from altair.app.ticketing.orders.models import Order, OrderedProductItemToken, OrderedProductItem
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID

logger = logging.getLogger(__name__)

csv_header = [
    ('no', u'NO'),
    ('selling_agency', u'販売元'),
    ('barcode_no', u'バーコード番号'),
    ('order_no', u'整理番号'),
    ('branch_no', u'チケット枝番'),
    ('last_name', u'氏名姓'),
    ('first_name', u'氏名名'),
    ('last_name_kana', u'姓（カナ）'),
    ('first_name_kana', u'名（カナ'),
    ('birthday', u'生年月日'),
    ('zip', u'郵便番号'),
    ('address_1', u'住所1'),
    ('address_2', u'住所2（建物名）'),
    ('tel_2', u'電話番号1'),  # 電話番号(携帯)
    ('tel_1', u'電話番号2'),  # 電話番号
    ('performance_date', u'公演日'),
    ('stock_type', u'席種'),
    ('seat_no', u'管理番号'),
    ('seat_name', u'席名'),
    ('ticket_count', u'チケット枚数'),
    ('delivery_method_name', u'チケット受取方法'),
    ('ticketing_store_name', u'発券コンビニ名'),
    ('exchange_number', u'コンビニ発券引換票番号'),
    ('issued', u'コンビニ発券状況')
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


def get_product_item_by_id(session, product_item_id):
    return session.query(ProductItem) \
        .filter_by(id=product_item_id) \
        .filter(ProductItem.deleted_at == None) \
        .one()


def get_ordered_product_item_by_id(session, ordered_product_item_id):
    return session.query(OrderedProductItem) \
        .filter_by(id=ordered_product_item_id) \
        .filter(OrderedProductItem.deleted_at == None) \
        .one()

def getDuplicatedBarcodeNo(export_data):
    barcodes = []
    for data in export_data:
        barcodes.append(data['barcode_no'])

    duplicates = []
    for b in barcodes:
        if barcodes.count(b) > 1 and b not in duplicates:
            duplicates.append(b)

    return duplicates

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-pid', '--performance_id', metavar='performance_id', type=str, required=True)
    parser.add_argument('-sid', '--sales_segment_id', metavar='sales_segment_id', type=str, required=True)

    args = parser.parse_args()
    bootstrap(args.config)
    session = get_session()

    try:
        if args.performance_id:
            pid = args.performance_id
            sid = args.sales_segment_id
            if sid:
                orders = session.query(Order) \
                    .filter(Order.sales_segment_id == sid) \
                    .filter(Order.canceled_at == None) \
                    .filter(Order.deleted_at == None) \
                    .filter(Order.refunded_at == None) \
                    .all()
            else:
                orders = session.query(Order) \
                    .filter(Order.performance_id == pid) \
                    .filter(Order.canceled_at == None) \
                    .filter(Order.deleted_at == None) \
                    .filter(Order.refunded_at == None) \
                    .all()

            # orderからcsv出力するためのdictへ変換
            export_data = []

            # 「NO」項目カウント
            j = 1

            for order in orders:

                birthday = None
                if order.user.user_profile and order.user.user_profile.birthday:
                    birthday = u"{0.year}/{0.month}/{0.day}".format(order.user.user_profile.birthday)

                address_1 = order.shipping_address.prefecture + order.shipping_address.city + order.shipping_address.address_1

                # ordersからコンビニ発券なもののみ処理
                # sejの場合
                if order.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
                    sej_order = order.sej_order
                    for i, ticket in enumerate(sej_order.tickets):
                        try:
                            if not ticket.ordered_product_item_token:
                                logger.warn('SejTicket.barcode_number={} has no relation with token.'.format(
                                    ticket.barcode_number))
                                continue

                            stock_type = None
                            if not ticket.ordered_product_item_token.seat:
                                product_item_id = ticket.product_item_id
                                product_item = get_product_item_by_id(session, product_item_id)
                                stock_type = product_item.stock_type

                            if not stock_type:
                                stock_type_id = ticket.ordered_product_item_token.seat.stock.stock_type_id
                                stock_type = get_stock_type_by_id(session, stock_type_id)

                            seat_no = '管理番号なし'
                            seat_name = '席名なし'
                            if ticket.ordered_product_item_token.seat and ticket.ordered_product_item_token.seat.seat_no:
                                seat_no = ticket.ordered_product_item_token.seat.seat_no.encode('utf-8')
                                seat_name = ticket.ordered_product_item_token.seat.name.encode('utf-8')

                        except NoResultFound:
                            logger.warn(
                                'no result was found for StockType.id={}.(Order.order_no={}, SejTicket.id={})'.format(
                                    stock_type_id, order.order_no, sej_order.id))
                            continue

                        retval = dict(
                            no=j,
                            selling_agency='楽天チケット',
                            barcode_no=ticket.barcode_number,
                            order_no=order.order_no,
                            branch_no=i + 1,
                            performance_date=order.performance.start_on,
                            stock_type=stock_type.name.encode('utf-8'),
                            seat_no=seat_no,
                            seat_name=seat_name,
                            last_name=order.shipping_address.last_name.encode('utf-8'),
                            first_name=order.shipping_address.first_name.encode('utf-8'),
                            last_name_kana=order.shipping_address.last_name_kana.encode('utf-8'),
                            first_name_kana=order.shipping_address.first_name_kana.encode('utf-8'),
                            birthday=birthday,
                            zip=order.shipping_address.zip,
                            address_1=address_1.encode('utf-8'),
                            address_2=order.shipping_address.address_2.encode('utf-8'),
                            tel_2=order.shipping_address.tel_2,
                            tel_1=order.shipping_address.tel_1,
                            delivery_method_name=order.payment_delivery_method_pair.delivery_method.name.encode(
                                'utf-8'),
                            ticketing_store_name='セブンイレブン',
                            exchange_number=sej_order.exchange_number or sej_order.billing_number,
                            issued='発券済み' if order.issued else '未発券',
                            ticket_count=len(sej_order.tickets),
                        )
                        j += 1
                        logger.info(
                            'barcode_num={}, order_no={}'.format(retval.get('barcode_no'), retval.get('order_no')))
                        export_data.append(retval)

                # famiportの場合
                elif order.delivery_plugin_id == FAMIPORT_DELIVERY_PLUGIN_ID:
                    fm_order = order.famiport_order
                    ticket_likes = fm_order.get('famiport_tickets')
                    for i, ticket_like in enumerate(ticket_likes):
                        try:
                            if not ticket_like.get('userside_token_id'):
                                logger.warn('FamiPortTicket.barcode_number={} has no relation with token.'.format(
                                    ticket_like.get('barcode_number')))
                                continue
                            token = get_token_by_id(session, ticket_like.get('userside_token_id'))

                            stock_type = None
                            if not token.seat:
                                ordered_product_item_id = token.ordered_product_item_id
                                ordered_product_item = get_ordered_product_item_by_id(session, ordered_product_item_id)
                                stock_type = ordered_product_item.product_item.stock_type

                            if not stock_type:
                                stock_type_id = token.seat.stock.stock_type_id
                                stock_type = get_stock_type_by_id(session, stock_type_id)

                            seat_no = '管理番号なし'
                            seat_name = '席名なし'
                            if token.seat and token.seat.seat_no:
                                seat_no = token.seat.seat_no.encode('utf-8')
                                seat_name = token.seat.name.encode('utf-8')

                        except NoResultFound:
                            logger.warn(
                                'no result was found for StockType.id={}.(Order.order_no={}, FamiPortTicket.id={})'.format(
                                    stock_type_id, order.order_no, ticket_like.get('id')))
                            continue

                        # famiportのバーコード番号には固定値で1が付与される。バーコード印字のタイミングでFM側で付与するものなのでチケスタDB内では付与されていない。
                        retval = dict(
                            no=j,
                            selling_agency='楽天チケット',
                            barcode_no='{0}{1}'.format('1', ticket_like.get('barcode_number')),
                            order_no=order.order_no,
                            branch_no=i + 1,
                            performance_date=order.performance.start_on,
                            stock_type=stock_type.name.encode('utf-8'),
                            seat_no=seat_no,
                            seat_name=seat_name,
                            last_name=order.shipping_address.last_name.encode('utf-8'),
                            first_name=order.shipping_address.first_name.encode('utf-8'),
                            last_name_kana=order.shipping_address.last_name_kana.encode('utf-8'),
                            first_name_kana=order.shipping_address.first_name_kana.encode('utf-8'),
                            birthday=birthday,
                            zip=order.shipping_address.zip,
                            address_1=address_1.encode('utf-8'),
                            address_2=order.shipping_address.address_2.encode('utf-8'),
                            tel_2=order.shipping_address.tel_2,
                            tel_1=order.shipping_address.tel_1,
                            delivery_method_name=order.payment_delivery_method_pair.delivery_method.name.encode(
                                'utf-8'),
                            ticketing_store_name='ファミリーマート',
                            exchange_number=fm_order['payment_reserve_number'].encode('utf-8'),
                            issued='発券済み' if order.issued else '未発券',
                            ticket_count=len(fm_order['famiport_tickets'])
                        )
                        j += 1
                        logger.info(
                            'barcode_num={}, order_no={}'.format(retval.get('barcode_no'), retval.get('order_no')))
                        export_data.append(retval)

            logger.info(u'{} orders was found.'.format(len(orders)))
            logger.info(u'start exporting csv...')

            # barcode_noの重複チェック
            duplicates = getDuplicatedBarcodeNo(export_data)
            if duplicates:
                raise Exception('Found duplicated barcode numbers as follows. {}'.format(', '.join(duplicates)))

            try:
                # export_dataをcsvとして書き出す
                filename = 'barcode_csv_{0:%Y%m%d-%H%M%S}.csv'.format(datetime.now())
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
