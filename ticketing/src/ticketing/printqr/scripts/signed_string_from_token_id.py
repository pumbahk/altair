# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlahelper
import argparse
from ticketing.core.models import TicketPrintHistory
from pyramid.registry import global_registry as registry
import ticketing.qr

def qr_from_history(config, history):
    ticket = history
    ticket.seat = ticket.seat
    ticket.performance = ticket.ordered_product_item.product_item.performance
    ticket.event = ticket.performance.event
    ticket.product = ticket.ordered_product_item.ordered_product.product
    ticket.order = ticket.ordered_product_item.ordered_product.order
    ticket.item_token = ticket.item_token

    params = dict(serial=("%d" % ticket.id),
                  performance=ticket.performance.code,
                  order=ticket.order.order_no,
                  date=ticket.performance.start_on.strftime("%Y%m%d"),
                  type=ticket.product.id)
    if ticket.seat:
        params["seat"] =ticket.seat.l0_id
        params["seat_name"] = ticket.seat.name
    else:
        params["seat"] = ""
        params["seat_name"] = "" #TicketPrintHistoryはtokenが違えば違うのでuniqueなはず
    builder = ticketing.qr.get_qrdata_builder(config)
    return builder.sign(builder.make(params))

def signed_seed(config, token_id):
    history = TicketPrintHistory.query.filter_by(item_token_id=token_id).first()
    if history is None:
        return "none"
    return qr_from_history(config, history)

def main():
    parser = argparse.ArgumentParser(description="sync page data to solr")
    parser.add_argument("--dburl", help="db url. e.g. mysql+pymysql://foo:foo@localhost/foo (default: %(default)s)", default="sqlite://")
    parser.add_argument("tokens", nargs="+", help="OrderedProductItemToken.id")
    args = parser.parse_args()
    _main(args)

def _main(args):
    setup(args.dburl)
    class config:
        registry = registry
    ticketing.qr.includeme(config)

    for token_id in args.tokens:
        print signed_seed(config, token_id)

def setup(dburl):
    engine = sa.create_engine(dburl)
    sqlahelper.add_engine(engine)
    return

if __name__ == "__main__":
    main()
