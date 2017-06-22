#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import logging
import sqlahelper

from altair.app.ticketing.core.models import TicketPrintHistory


logger = logging.getLogger(__name__)
DBSession = sqlahelper.get_session()

select_order_id_sql = """
                        select id as order_id from `Order` 
                        where 
                            organization_id = '107'
                        AND NOT EXISTS (
                            select order_id as id from TicketPrintHistory
                            where TicketPrintHistory.order_id = `Order`.id
                        )
                      """

select_code_sql = """
    select
        OPIT.seat_id AS seat_id,
        OPIT.id AS item_token_id, 
        OPI.id AS ordered_product_item_id,
        ODR.id AS order_id, 
        OPT.product_id
    from `Order` ODR INNER JOIN OrderedProduct OPT
        ON ODR.id = OPT.order_id 
        AND ODR.organization_id = '107'
        AND ODR.id = %s
    INNER JOIN OrderedProductItem OPI
        ON OPT.product_id = OPI.ordered_product_id
    INNER JOIN OrderedProductItemToken OPIT
        ON OPIT.ordered_product_item_id = OPI.id
"""



def main(request):
    print "楽天トラベルチケットヒストリーチェック開始"
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
    cur.execute(select_order_id_sql)
    order_data = cur.fetchall()
    if ticket_history_com(cur, order_data):
        print "commit()実行してからqr_code_userを実行してください。"
    else:
        print "qr_code_userを実行してください。"

def ticket_history_com(cur, order_data):
    if order_data is None:
        return False
    for od in order_data:
        cur.execute(select_code_sql, od[0])
        code_data = cur.fetchall()
        for cd in code_data:
            history = TicketPrintHistory(
                seat_id=cd[0],
                item_token_id=cd[1],
                ordered_product_item_id=cd[2],
                order_id=cd[3]
            )
            DBSession.add(history)
            DBSession.flush()
    return True

if __name__ == '__main__':
    main()