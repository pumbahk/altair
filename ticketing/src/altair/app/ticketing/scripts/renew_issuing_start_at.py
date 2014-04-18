# encoding: utf-8
import sys
import itertools
import logging
import argparse
import re
import csv
from datetime import datetime
from dateutil.parser import parse as parsedate
from sqlalchemy.sql.expression import desc
import sqlahelper
from paste.deploy import loadapp
from pyramid.paster import bootstrap, setup_logging
import transaction

logger = logging.getLogger(__name__)

formats = {
    'csv': csv.excel,
    'tsv': csv.excel_tab,
    }

class ApplicationException(Exception):
    pass

class RecordError(ApplicationException):
    @property
    def message(self):
        return self.args[0]
 
    @property
    def lineno(self):
        return self.args[1]
 
    def __str__(self):
        return '%s at line %d' % (self.message, self.lineno)

import locale
charset = locale.getpreferredencoding()

def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, (pad + msg).encode(charset)

def do_renew_issuing_start_at(request, session, file_, format, encoding):
    from altair.app.ticketing.orders.models import Order
    from altair.app.ticketing.orders.api import refresh_order
    now = datetime.now()
    f = open(file_)
    r = csv.reader(f, dialect=format)
    headers = [col.decode(encoding) for col in r.next()]
    l = 0

    def new_record_error(msg):
        raise RecordError(msg, l)

    def parse_datetime(s, msg=None):
        try:
            return parsedate(s)
        except Exception as e:
            raise new_record_error(str(e))
        assert False # never get here

    for l, row in enumerate(r, 2):
        try:
            cols = dict((headers[i], col.decode(encoding)) for i, col in enumerate(row))
            order_no = cols[u'order_no']
            new_issuing_start_at = parse_datetime(cols[u'issuing_start_at'])
            order = session.query(Order).filter_by(order_no=order_no).order_by(Order.branch_no).order_by(desc(Order.branch_no)).first()
            if order is None:
                raise new_record_error(u'Order %s not found' % order_no)
            message('creating a branch for Order %s to update issuing_start_at' % order_no)
            new_order = Order.clone(order, deep=True)
            new_order.issuing_start_at = new_issuing_start_at
            refresh_order(request, session, new_order)
            message('done processing Order %s' % order_no)
            transaction.commit()
        except:
            transaction.abort()
            raise

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='file', type=str)
    parser.add_argument('--config', metavar='config', type=str)
    parser.add_argument('--encoding', metavar='encoding', type=str)
    parser.add_argument('--format', metavar='format', type=str, default='csv')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']

    session = sqlahelper.get_session()

    format = formats.get(args.format)
    if format is None:
        message("unknown format: %s" % format)
        return 255

    try:
        do_renew_issuing_start_at(request, session, args.file, format, (args.encoding or charset))
    except ApplicationException as e:
        message(e.message) 
        return

if __name__ == '__main__':
    main()

# vim: sts=4 sw=4 ts=4 et ai
