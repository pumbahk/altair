#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import argparse
import pymysql

import logging
logger = logging.getLogger(__name__)

# from collections import OrderedDict
# import pymysql.cursors
# from datetime import datetime
# from collections import OrderedDict
# from datetime import datetime
# from collections import OrderedDict
# import pymysql
# from deploy.dev.parts.omelette.sqlalchemy.dialects.mysql import pymysql
# import pymysql
# from pymysql.tests import base

from altair.app.ticketing.core.models import TicketPrintHistory
from altair.app.ticketing.qr.utils import make_data_for_qr,

from altair.app.ticketing.qr.builder import qr

class fins(csv.Dialect):
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL

csv.register_dialect('fins', fins)


def main():
    # 日本語使えるところまでもっていけなかったので、ステータスが英語で出力される。
    # CSVを出力したあとに、置換してあげると優しい
    parser = argparse.ArgumentParser(description=u'申し込まれた抽選のエントリを、CSVで出力する')
    parser.add_argument('-n', "--lot", required=True, help=u'')
    print "LotsEntry Download!!"
    args = parser.parse_args()

    save_entries(args)


def save_entries(args):

    # develop
    #host = 'localhost'
    #db = 'ticketing'
    #user = 'ticketing'
    #password = 'ticketing'
    #port = 3306

    host = 'dbmain.standby.altr'
    db = 'ticketing'
    user = 'ticketing_ro'
    password = 'ticketing'
    port = 3308

    client = pymysql.connect(host=host, db=db, user=user, passwd=password, port=port)
    cur = client.cursor()
    cur.execute('SET NAMES sjis')

    wf = open(str(args.lot) + '.csv', 'w+b')
    writer = csv.writer(wf, dialect='fins')

    sql = get_sql().format(args.lot, args.lot)

    cur.execute(sql)
    datas = cur.fetchall()
    creat_qr_url(datas)
    write_result(writer, datas)

def build_qr_by_history(history):
    logger.debug("PARAM========111>>>")
    logger.debug(vars(history))
    logger.debug(vars(history._sa_instance_state))
    params, ticket = make_data_for_qr(history)
    logger.debug("PARAM========22>>>")
    logger.debug(params["seat"])
    logger.debug(params["seat_name"])
    logger.debug(params["type"])
    builder = qr()
    ticket.qr = builder.sign(builder.make(params))
    ticket.sign = ticket.qr[0:8]
    logger.debug(ticket.qr)
    logger.debug(ticket.sign)
    logger.debug("PARAM========33>>>")
    return ticket

def creat_qr_url(datas):

    qr_url = []
    for dt in datas:
        history = TicketPrintHistory(
            seat_id=dt.seat_id,
            item_token_id=dt.item_token_id,
            ordered_product_item_id=dt.ordered_product_item_id,
            order_id=dt.order_id
        )
        ticket = build_qr_by_history(history)

        qr_url.append("https://tq.tstar.jp/orderreview/qr/"+qr.id+"/"+qr.sign+"/")
    return qr_url

def write_result(writer, datas):
    header = u"OrderNo", u"TicketPrintHistoryId", u"OrderedProductItemId", u"SeatId", u"ItemTokenId", u"OrderId", u"ShipAddId", u"UserName"
    header = map(lambda name: name.encode('sjis'), header)
    writer.writerow(header)

    for row in datas:
        writer.writerow(row)

def get_sql():
    sql = u"""\
SELECT
    ODR.order_no AS `order_no`,
    TPH.id AS `ticketPrintHistory_id`, 
    TPH.ordered_product_item_id AS `ordered_product_item_id`, 
    TPH.seat_id AS `seat_id`, 
    TPH.item_token_id AS `item_token_id`,
    TPH.order_id AS `order_id`,
    SAS.id AS `shipAdd_id`, 
    CONCAT(SAS.last_name, ' ', SAS.first_name, ' (',SAS.last_name_kana, ' ',SAS.first_name_kana,')') AS `UserName`
from `Order` ODR 
INNER JOIN TicketPrintHistory TPH 
    ON TPH.order_id = ODR.id 
    AND ODR.organization_id = '107'
INNER JOIN ShippingAddress SAS 
    ON ODR.shipping_address_id = SAS.id
    
"""
    return sql

if __name__ == '__main__':
    main()
