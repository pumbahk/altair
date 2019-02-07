#! /usr/bin/env python
#-*- coding: utf-8 -*-
import argparse
import csv
import logging
import sys

import transaction
from altair.app.ticketing.core.models import Stock_drawing_l0_id, StockHolder, Stock, StockType
from altair.app.ticketing.models import DBSession
from pyramid.paster import bootstrap

logger = logging.getLogger(__name__)


def main(argv=sys.argv[1:]):
    """
    紐付いているリージョンを全て消して、CSVのリージョンを入れるスクリプト

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-f', '--file_name', metavar='file_name', type=str, required=True)
    parser.add_argument('-e', '--event_id', metavar='event_id', type=str, required=True)
    parser.add_argument('-p', '--performance_id', metavar='performance_id', type=str, required=True)

    args = parser.parse_args()
    env = bootstrap(args.config)

    try:
        f = open(args.file_name, 'r')
        reader = csv.reader(f)
        for row in reader:
            sh = StockHolder.query.filter(StockHolder.name.like('%自社%'))\
                .filter(StockHolder.event_id == args.event_id).first()

            stock = Stock.query.join(StockType, Stock.stock_type_id == StockType.id)\
                .join(StockHolder, StockHolder.id == Stock.stock_holder_id)\
                .filter(StockHolder.id == sh.id)\
                .filter(Stock.performance_id == args.performance_id)\
                .filter(StockType.name == row[0]).first()

            if not stock:
                continue

            for drawing in stock.stock_drawing_l0_ids:
                DBSession.delete(drawing)

            sd = Stock_drawing_l0_id()
            sd.stock_id = stock.id
            sd.drawing_l0_id = row[1]
            DBSession.add(sd)
        transaction.commit()
    finally:
        transaction.abort()


if __name__ == '__main__':
    main(sys.argv[1:])

