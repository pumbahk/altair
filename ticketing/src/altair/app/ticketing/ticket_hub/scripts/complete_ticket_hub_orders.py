# -*- coding: utf-8 -*-
"""TicketHubOrder(QRゲート入場)を完了状態にするタスク

"""
import sys
import logging
import argparse
from pyramid.paster import bootstrap, setup_logging
from altair.multilock import (
    MultiStartLock,
    AlreadyStartUpError,
    )
import sqlahelper
from altair.sqlahelper import get_global_db_session
from altair.ticket_hub.api import TicketHubClient, TicketHubAPI
from ..models import TicketHubOrder


_logger = logging.getLogger(__file__)

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
    request = env['request']
    session = sqlahelper.get_session()
    api = setup_ticket_hub_api(registry)

    _logger.info('ticket hub complete order start')
    orders = session.query(TicketHubOrder) \
                    .filter_by(completed_at=None) \
                    .order_by(TicketHubOrder.created_at.desc()) \
                    .limit(1)

    for order in orders:
        _logger.info(vars(order))
        completed = order.complete(api)
        _logger.info(completed)

    _logger.info('ticket hub complete order end')

if __name__ == u"__main__":
    sys.exit(main())
