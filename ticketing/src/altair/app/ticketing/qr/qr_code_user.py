#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import pymysql
import logging
import sqlahelper

from altair.app.ticketing.core.models import TicketPrintHistory
from altair.app.ticketing.qr.utils import make_data_for_qr
from altair.app.ticketing.qr import get_qrdata_builder

logger = logging.getLogger(__name__)
DBSession = sqlahelper.get_session()

select_qr_sql = """
                       SELECT
                           TPH.seat_id AS `seat_id`, 
                           TPH.item_token_id AS `item_token_id`,
                           TPH.ordered_product_item_id AS `ordered_product_item_id`, 
                           TPH.order_id AS `order_id`,
                           ODR.order_no AS `order_no`,
                           TPH.id AS `ticketPrintHistory_id`, 
                           SAS.id AS `shipAdd_id`, 
                           CONCAT(SAS.last_name, ' ', SAS.first_name, ' (',SAS.last_name_kana, ' ',
                           SAS.first_name_kana,')') AS `UserName`
                       from `Order` ODR
                           INNER JOIN TicketPrintHistory TPH 
                           ON TPH.order_id = ODR.id 
                           AND ODR.organization_id = '107'
                           AND TPH.seat_id IS NOT NULL
                           AND TPH.item_token_id IS NOT NULL
                           AND TPH.ordered_product_item_id IS NOT NULL
                           AND TPH.order_id IS NOT NULL
                        INNER JOIN ShippingAddress SAS
                           ON ODR.shipping_address_id = SAS.id
                       """

def main(request):
    print "楽天トラベルQR CODE URLリスト作成"
    save_entries(request)

def save_entries(request):
    # develop
    # host = '127.0.0.1'
    # db = 'ticketing'
    # user = 'ticketing'
    # password = 'ticketing'
    # port = 3306

    host = 'dbmain.standby.altr'
    db = 'ticketing'
    user = 'ticketing_ro'
    password = 'ticketing'
    port = 3308

    client = pymysql.connect(host=host, db=db, user=user, passwd=password, port=port, charset='utf8')
    cur = client.cursor()
    wf = open(str('resQrCode') + '.csv', 'w+b')
    writer = csv.writer(wf, lineterminator='\n')
    cur.execute(select_qr_sql)
    datas = cur.fetchall()
    qr_url_arr = creat_qr_url(request, datas)
    write_result(writer, datas, qr_url_arr)

def build_qr_by_history(request, history):
    params, ticket = make_data_for_qr(history)
    builder = get_qrdata_builder(request)
    ticket.qr = builder.sign(builder.make(params))
    ticket.sign = ticket.qr[0:8]
    return ticket

def creat_qr_url(request,datas):
    qr_url = []
    for dt in datas:
        print dt[3]
        history = TicketPrintHistory(
            seat_id=dt[0],
            item_token_id=dt[1],
            ordered_product_item_id=dt[2],
            order_id=dt[3]
        )
        DBSession.add(history)
        ticket = build_qr_by_history(request, history)
        qr_url.append('https://tq.tstar.jp/orderreview/qr/'+str(ticket.id)+'/'+ticket.sign+'/')
    return qr_url

def write_result(writer, datas, qr_url_arr):
    header = u"予約番号", u"氏名", u"QR_URL"
    header = map(lambda name: name.encode('sjis'), header)
    writer.writerow(header)
    cnt = 0
    for row in datas:
        writer.writerow(list((row[4], row[7].encode('sjis'), qr_url_arr[cnt])))
        cnt = cnt + 1
    return 0

if __name__ == '__main__':
    main()