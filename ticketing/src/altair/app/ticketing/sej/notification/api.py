# coding: utf-8

import logging
from sqlalchemy.sql.expression import desc
from altair.app.ticketing.sej.api import get_sej_order_by_exchange_number_or_billing_number

__all__ = [ 
    'fetch_notifications',
    ]

logger = logging.getLogger(__name__)

def fetch_notifications():
    from ..models import _session
    from .models import SejNotification
    for notification in _session.query(SejNotification).filter_by(reflected_at=None):
        sej_order = get_sej_order_by_exchange_number_or_billing_number(
            session=_session,
            order_no=notification.order_no or None, # 空文字を None にしたい
            exchange_number=notification.exchange_number or None,
            billing_number=notification.billing_number or None
            )
        if sej_order is not None:
            yield sej_order, notification
        else:
            logger.error("SejOrder Not found: order_no=%s, exchange_number=%s, billing_number=%s" % (notification.order_no, notification.exchange_number,notification.billing_number))
