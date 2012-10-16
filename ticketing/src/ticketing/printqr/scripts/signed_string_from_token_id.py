# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlahelper
import argparse
from pyramid.registry import global_registry as registry
import ticketing.qr
from ticketing.qr import get_qrdata_builder
from ticketing.qr.utils import get_matched_token_query_from_order_no
from ticketing.qr.utils import get_or_create_matched_history_from_token
from ticketing.qr.utils import make_data_for_qr

def _signed_string_from_history(builder, history):
    params = make_data_for_qr(history)
    return builder.sign(builder.make(params))

def print_signed_string(builder, order_no):
    for token in get_matched_token_query_from_order_no(order_no):
        history = get_or_create_matched_history_from_token(order_no, token)
        print _signed_string_from_history(builder, history)

def main():
    parser = argparse.ArgumentParser(description="sync page data to solr")
    parser.add_argument("--dburl", help="db url. e.g. mysql+pymysql://foo:foo@localhost/foo (default: %(default)s)", default="sqlite://")
    parser.add_argument("order_nos", nargs="+", help="Ordere.order_no")
    args = parser.parse_args()
    _main(args)

def _main(args):
    setup(args.dburl)
    class config:
        registry = registry
    ticketing.qr.includeme(config)
    builder = get_qrdata_builder(config)

    for order_no in args.order_nos:
        print_signed_string(builder, order_no)

def setup(dburl):
    engine = sa.create_engine(dburl)
    sqlahelper.add_engine(engine)
    return

if __name__ == "__main__":
    main()
