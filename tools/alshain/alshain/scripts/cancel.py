#-*- coding: utf-8 -*-
import sys
import time
import argparse
import datetime
try:
    import stringio
except ImportError:
    import StringIO as stringio
import pyramid.request
import pyramid.paster
import pyramid.testing
import transaction
import mako.template
import altair.sqlahelper
from altair.app.ticketing.core.models import (
    Event,
    Performance,
    PaymentMethod,
    DeliveryMethod,
    PaymentDeliveryMethodPair,
    )
from altair.app.ticketing.orders.models import Order


BACKUP_FILE_NAME = time.strftime('order_cancel_backup_%Y%m%d_%H%M%S.csv')

PAYMENT_INNER = 4 # inner payment type (plugin)
DELIVERY_INNER = 3 # inner delivery type (plugin)

CANCEL_DATA_DETAIL_TEMPLATE = """
**************************************************
CANCEL DETAIL
**************************************************
<%
 performances = set([order.performance for order in orders])
 events = set([performance.event for performance in performances])
 first_last_mail = set([(order.shipping_address.first_name, order.shipping_address.last_name, order.shipping_address.email_1)
     for order in orders if order.shipping_address])
 payment_plugins = set([order.payment_delivery_method_pair.payment_method.payment_plugin
     for order in orders])
 delivery_plugins = set([order.payment_delivery_method_pair.delivery_method.delivery_plugin
     for order in orders])
 %>

EVENTS
==========================

%for event in events:
 - ${event.id} ${event.title}
%endfor

PERFORMANCE
==========================

%for performance in performances:
 - ${performance.id} ${performance.name}
%endfor

SHIPPING ADDRESS
==========================

%for first, last, email in first_last_mail:
 - ${first} ${last} ${email}
%endfor

PAYMENT PLUGIN
==========================

%for plugin in payment_plugins:
 - ${plugin.id} ${plugin.name}
%endfor

DELIVERY PLUGIN
==========================

%for plugin in delivery_plugins:
 - ${plugin.id} ${plugin.name}
%endfor

TOTAL
==========================

${len(orders)} order
"""


class ShouldSpecifyParameterError(ValueError):
    message = """\
Should specify the parameters at least one.
need following:

 --event
 --performance
 --date

"""

class IllegalFormatDatetimeError(Exception):
    pass

def str2datetime(text):
    fmts = ['%Y', '%m', '%d', '%H', '%M', '%S']
    for ii in range(len(fmts)):
        fmt = ''.join(fmts[:-ii])
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise IllegalFormatDatetimeError(text)

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    parser.add_argument('--event', default=0, type=int)
    parser.add_argument('--performance', default=None)
    parser.add_argument('--date', default=None)
    parser.add_argument('--organization-code', dest='organization_code', default='QA')
    parser.add_argument('--no-backup', dest='no_backup', default=False)
    opts = parser.parse_args(argv)

    if not (opts.event or opts.performance or opts.date):
        parser.error(ShouldSpecifyParameterError.message)

    pyramid.paster.setup_logging(opts.conf)
    env = pyramid.paster.bootstrap(opts.conf)
    settings = env['registry'].settings
    request = pyramid.testing.DummyRequest()
    session = altair.sqlahelper.get_db_session(request, 'slave')

    qs = Order.query\
      .join(Performance)\
      .join(Event)\
      .join(PaymentDeliveryMethodPair)\
      .join(PaymentMethod)\
      .join(DeliveryMethod)\
      .filter(Order.canceled_at==None)\
      .filter(PaymentMethod.payment_plugin_id==PAYMENT_INNER)\
      .filter(DeliveryMethod.delivery_plugin_id==DELIVERY_INNER)

    if opts.event:
        event_id = opts.event
        qs = qs.filter(Event.id==event_id)

    if opts.performance:
        ids = map(int, opts.performance.split(','))
        qs = qs.filter(Performance.id.in_(ids))

    if opts.date:
        if opts.date.endswith(':'):
            opts.date += ':'
            start_end = opts.date.split(':')

            start = str2datetime(start_end[0])
            qs = qs.filter(Order.created_at > start)

            if count == 2:
                end = str2datetime(start_end[1])
                qs = qs.filter(Order.created_at < end)
            elif count > 2:
                parser.error('invalid format: {}'.format(opts.date))

    orders = qs.all()

    tmpl = mako.template.Template(CANCEL_DATA_DETAIL_TEMPLATE)
    print(tmpl.render(orders=orders))
    word = raw_input('OK? (yes/no)')

    if word == 'yes':
        fp = None
        if opts.no_backup:
            fp = stringio.StringIO()
        else:
            fp = open(BACKUP_FILE_NAME, 'w+b')

        for order in orders:
            txt = '{} ->'.format(order.order_no)
            fp.write(txt)
            print(txt)

            status = order.cancel(request)

            txt = '{}\n'.format(status)
            fp.write(txt)
            print(txt)
        fp.close()
    else:
        print('bye')

if __name__ == '__main__':
    main()
