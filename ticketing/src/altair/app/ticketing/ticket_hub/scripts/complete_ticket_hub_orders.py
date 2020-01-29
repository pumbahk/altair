# -*- coding: utf-8 -*-
"""TicketHubOrder(QRゲート入場)を完了状態にするタスク

"""
import sys
import logging
import argparse
from pyramid.paster import bootstrap, setup_logging
import sqlahelper
from altair.ticket_hub.api import TicketHubClient, TicketHubAPI
from altair.ticket_hub.exc import TicketHubAPIError
from ..models import TicketHubOrder
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.models import DBSession


logger = logging.getLogger(__name__)

def setup_ticket_hub_api(registry):
    settings = registry.settings
    return TicketHubAPI(TicketHubClient(
        base_uri=settings["altair.tickethub.base_uri"],
        api_key=settings["altair.tickethub.api_key"],
        api_secret=settings["altair.tickethub.api_secret"],
        seller_code=settings["altair.tickethub.seller_code"],
        seller_channel_code=settings["altair.tickethub.seller_channel_code"]
    ))

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--stdout', default=False, action='store_true')
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    args = parser.parse_args(argv)

    if not args.stdout:
        setup_logging(args.config)

    env = bootstrap(args.config)
    registry = env['registry']
    api = setup_ticket_hub_api(registry)

    logger.info('ticket hub complete order start')

    # 多重起動防止
    LOCK_NAME = main.__name__
    LOCK_TIMEOUT = 10
    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status != 1:
        logger.warn('lock timeout: already running process')
        return
    try:
        query = DBSession.query(TicketHubOrder) \
            .join(Order) \
            .filter(TicketHubOrder.completed_at.is_(None)) \
            .filter(Order.paid_at.isnot(None))

        if query.count() == 0:
            # 対象なし
            logging.info('ticket hub complete order is nothing. skip...')

        ticket_hub_orders = query.all()
        for ticket_hub_order in ticket_hub_orders:
            try:
                ticket_hub_order.complete(api)
            except TicketHubAPIError as e:
                logger.error(e.message)
                logger.error('Failed to complete TicketHubOrder. order_no = %s, altair_order_no = %s',
                             ticket_hub_order.order_no, ticket_hub_order.altair_order_no)
                continue

    except Exception as e:
        logger.error(e.message)

    conn.close()
    logger.info('ticket hub complete order end')


if __name__ == u"__main__":
    sys.exit(main())
