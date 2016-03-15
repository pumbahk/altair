# -*- coding:utf-8 -*-
from altair.sqlahelper import get_db_session
from altair.app.ticketing.orders.models import OrderedProductItemToken


def can_use_coupon(request, token_id):
    session = get_db_session(request, name="slave")
    token = session.query(OrderedProductItemToken).filter(OrderedProductItemToken.id == token_id).first()
    if not token:
        return False
    if token.printed_at:
        return False
    return True
