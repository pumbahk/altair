#-*- coding: utf-8 -*-
import datetime
from altair.app.ticketing.core.models import (
    Order,
    Performance,
    )

class CannotCancel(Exception):
    pass

def safe_cancel(request):
    start_at = datetime.datetime(2014, 4, 5, 0, 0, 0)
    performance_ids = [8326, 8327, 8328, 8329]
    orders = Order.query.join(Performance)\
        .filter(Order.created_at>start_at)\
        .filter(Order.canceled_at==None)\
        .filter(Performance.id.in_(performance_ids))\
        .all()

    print '='*20
    print 'Performance'
    print '='*20
    print "\n"

    names = list(set([order.performance.name  for order in orders]))
    for name in names:
        print name


    print '='*20
    print 'ShippingAddress'
    print '='*20
    print "\n"

    names = list(set([(order.shipping_address.last_name, order.shipping_address.first_name) for order in orders]))
    for lname, fname in names:
        print lname, fname

    print '='*20
    print 'Check Payment Plugin and Delivery Plugin'
    print '='*20
    print "\n"

    ok = True
    for order in orders:
        if order.payment_delivery_pair.payment_method.payment_plugin_id != 4 \
                or order.payment_delivery_pair.delivery_method.delivery_plugin_id != 3:
            print 'ID order_no Payment Delivery:', order.id, order.order_no, \
                order.payment_delivery_pair.payment_method.payment_plugin_id, \
                order.payment_delivery_pair.delivery_method.delivery_plugin_id
            ok = False

    if not ok:
        raise CannotCancel()
    else:
        print '-> OK'

    names = list(set([(order.shipping_address.last_name, order.shipping_address.first_name) for order in orders]))
    for lname, fname in names:
        print lname, fname



    raw_input('Cancel?')

    with open('/tmp/cancel.txt', 'w+b') as fp:
        try:
            fp.write('CANCEL START\n')
            for order in orders:
                fp.write(order.order_no)
                status = order.cancel(request)
                fp.write(' {}\n'.format(status))
                print order.order_no, status
        except:
            fp.write(' NG\n')
