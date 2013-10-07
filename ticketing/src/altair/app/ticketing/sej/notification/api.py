# coding: utf-8

from sqlalchemy.sql.expression import desc

__all__ = [ 
    'fetch_notifications',
    ]

def get_sej_order(notification):
    from ..models import SejOrder
    q = SejOrder.filter_by(order_no=notification.order_no)
    if notification.exchange_number:
        q = q.filter_by(exchange_number=notification.exchange_number)
    if notification.billing_number:
        q = q.filter_by(billing_number=notification.billing_number)
    return q.order_by(desc(SejOrder.branch_no)).limit(1).first()

def get_order(sej_order):
    from altair.app.ticketing.core.models import Order
    return Order.filter_by(order_no=sej_order.order_no).first()

def fetch_notifications():
    from .models import SejNotification
    for notification in SejNotification.filter_by(reflected_at=None):
        sej_order = get_sej_order(notification)
        if sej_order:
            order = get_order(sej_order)
            yield sej_order, order, notification
        else:
            logging.error("SejOrder Not found: order_no=%s, exchange_number=%s, billing_number=%s" % (notification.order_no, notification.exchange_number,notification.billing_number))
