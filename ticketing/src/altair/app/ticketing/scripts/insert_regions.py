#! /usr/bin/env python
#-*- coding: utf-8 -*-
import argparse
import csv
import logging
import sys

import transaction
from altair.app.ticketing.core.models import Event, Stock_drawing_l0_id, StockHolder, Stock, StockType
from altair.app.ticketing.models import DBSession
from pyramid.paster import bootstrap

logger = logging.getLogger(__name__)


def add_region(event_id, performance_id, stocktype_name, drawing_l0_id):
        sh = StockHolder.query.filter(StockHolder.name.like('%自社%')) \
            .filter(StockHolder.event_id == event_id).first()

        stock = Stock.query.join(StockType, Stock.stock_type_id == StockType.id) \
            .join(StockHolder, StockHolder.id == Stock.stock_holder_id) \
            .filter(StockHolder.id == sh.id) \
            .filter(Stock.performance_id == performance_id) \
            .filter(StockType.name == stocktype_name).first()

        if not stock:
            return

        for drawing in stock.stock_drawing_l0_ids:
            DBSession.delete(drawing)

        sd = Stock_drawing_l0_id()
        sd.stock_id = stock.id
        sd.drawing_l0_id = drawing_l0_id
        DBSession.add(sd)


def main(argv=sys.argv[1:]):
    """
    紐付いているリージョンを全て消して、CSVのリージョンを入れるスクリプト

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-f', '--file_name', metavar='file_name', type=str, required=True)
    parser.add_argument('-e', '--event_id', metavar='event_id', type=str, required=True)
    parser.add_argument('-p', '--performance_id', metavar='performance_id', type=str, required=False)

    args = parser.parse_args()
    env = bootstrap(args.config)


    try:
        f = open(args.file_name, 'r')
        reader = csv.reader(f)
        for row in reader:
            if args.performance_id:
                # 特定のパフォーマンスのみにリージョンを入れる
                add_region(args.event_id, args.performance.id, row[0], row[1])
            else:
                # 指定されたイベント以下のパフォーマンスすべてにリージョンを入れる
                event = Event.query.filter(Event.id == args.event_id).first()
                for performance in event.performances:
                    add_region(args.event_id, performance.id, row[0], row[1])
        transaction.commit()
    finally:
        transaction.abort()


if __name__ == '__main__':
    main(sys.argv[1:])

