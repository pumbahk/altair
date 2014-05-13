# coding: utf-8

import logging
from sqlalchemy.sql.expression import desc

__all__ = [ 
    'fetch_notifications',
    ]

logger = logging.getLogger(__name__)

def get_sej_order(session, notification):
    from ..models import SejOrder
    q = session.query(SejOrder).filter_by(order_no=notification.order_no)
    if notification.exchange_number:
        q = q.filter_by(exchange_number=notification.exchange_number)
    if notification.billing_number:
        q = q.filter_by(billing_number=notification.billing_number)
    return q.order_by(desc(SejOrder.branch_no)).limit(1).first()

def get_order(session, sej_order):
    from altair.app.ticketing.orders.models import Order
    return session.query(Order).filter_by(order_no=sej_order.order_no).first()

def fetch_notifications(session):
    if session is None:
        from ..models import _session
        session = _session
    from .models import SejNotification
    for notification in session.query(SejNotification).filter_by(reflected_at=None):
        sej_order = get_sej_order(session, notification)
        if sej_order:
            order = get_order(session, sej_order)
            yield sej_order, order, notification
        else:
            logger.error("SejOrder Not found: order_no=%s, exchange_number=%s, billing_number=%s" % (notification.order_no, notification.exchange_number,notification.billing_number))
