#! /usr/bin/env python
#-*- coding: utf-8 -*-
import csv
import sys
import time
import argparse
import altair.sqlahelper
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import (
    Event,
    )
from altair.app.ticketing.sej.models import (
    SejOrder,
    )
import pyramid.request
import pyramid.paster
import pyramid.testing
import transaction

BACKUP_FILE_NAME = time.strftime('sej_order_shop_id_backup_%Y%m%d_%H%M%S.csv')
DUMMY_SHOP_ID = '77777'

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    parser.add_argument('--no-backup', dest='no_backup', default=False)
    parser.add_argument('--shop_id', dest='shop_id', default=DUMMY_SHOP_ID)
    opts = parser.parse_args(argv)

    pyramid.paster.setup_logging(opts.conf)
    env = pyramid.paster.bootstrap(opts.conf)
    settings = env['registry'].settings

    if not opts.no_backup:
        request = pyramid.testing.DummyRequest()
        session = altair.sqlahelper.get_db_session(request, 'slave')
        columns = SejOrder.id, SejOrder.shop_id
        names = [str(column).replace('.', '_').lower() for column in columns]
        values = [values for values in session.query(*columns)]

        with open(BACKUP_FILE_NAME, 'w+b') as fp:
            writer = csv.writer(fp)
            writer.writerow(names)
            writer.writerows(values)

    sej_order_table = DBSession.query(SejOrder)
    sej_order_table.update(values={'shop_id': opts.shop_id})
    transaction.commit()

if __name__ == '__main__':
    main()
