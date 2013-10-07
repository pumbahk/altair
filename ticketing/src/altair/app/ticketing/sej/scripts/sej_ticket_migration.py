# -*- coding:utf-8 -*-

import logging
import transaction
import argparse

from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.sql.expression import and_, not_, or_

from altair.app.ticketing.core.models import Order
from altair.app.ticketing.sej.models import SejOrder, SejTicket

def update_product_item_id():
    ''' SejTicket.product_item_idをセットする
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('-f')
    parser.add_argument('-t')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)

    term_from = args.f
    term_to = args.t

    logging.info('start update_product_item_id')
    logging.info('from=%s, to=%s' % (term_from, term_to))

    while True:
        # 有効な予約でSejTicket.product_item_idが空のものを1件ずつ処理
        query = Order.query.filter(Order.canceled_at==None, Order.deleted_at==None)\
            .join(SejOrder, SejOrder.order_id==Order.order_no)\
            .join(SejTicket, SejTicket.order_id==SejOrder.id)\
            .filter(SejTicket.product_item_id==None)

        if term_from:
            query = query.filter(term_from < Order.created_at)
        if term_to:
            query = query.filter(Order.created_at < term_to)

        order = query.first()
        if order is None:
            logging.info('not found')
            break

        try:
            order_no = order.order_no

            sej_ticket_query = SejTicket.query.filter(SejTicket.product_item_id==None)\
                .join(SejOrder, SejOrder.id==SejTicket.order_id)\
                .filter(SejOrder.order_id==order_no)\
                .order_by(SejTicket.ticket_idx)
            sej_tickets = sej_ticket_query.all()

            # ProductItemをカウント
            opi_count = 0
            for op in order.items:
                opi_count +=  len(op.ordered_product_items)

            for op in order.items:
                for opi in op.ordered_product_items:
                    if opi_count == 1:
                        # OrderにProductItemが1つのみなら全てそのidをセット
                        for i in range(len(sej_tickets)):
                            sej_ticket = sej_tickets.pop()
                            sej_ticket.product_item_id = opi.product_item_id
                            sej_ticket.save()
                            logging.info('success (order_no=%s, sej_ticket.id=%s, pi.id=%s)' % (order_no, sej_ticket.id, opi.product_item_id))
                    else:
                        # OrderにProductItemが複数あるケース
                        for i in range(opi.quantity):
                            if sej_tickets:
                                sej_ticket = sej_tickets.pop()
                                sej_ticket.product_item_id = opi.product_item_id
                                sej_ticket.save()
                                logging.info('success (order_no=%s, sej_ticket.id=%s, pi.id=%s)' % (order_no, sej_ticket.id, opi.product_item_id))
                            else:
                                logging.error('no sej_ticket (order_no=%s, opi.id=%s)' % (order_no, opi.id))
                                break
            if sej_tickets:
                logging.error('no product_item_id (order_no=%s)' % order_no)

            transaction.commit()
        except Exception, e:
            transaction.abort()
            logging.error('error: %s' % e)

    logging.info('end update_product_item_id')
