# -*- coding:utf-8 -*-
from altair.sqlahelper import get_db_session
from altair.app.ticketing.orders.models import OrderedProductItemToken
from altair.app.ticketing.core.models import Host

def can_use_coupon(request, token_id):
    session = get_db_session(request, name="slave")
    token = session.query(OrderedProductItemToken).filter(OrderedProductItemToken.id == token_id).first()
    if not token:
        return False
    if token.printed_at:
        return False
    return True

def get_host(request):
    session = get_db_session(request, name="slave")
    host = session.query(Host).filter(Host.organization_id == request.organization.id).first()
    return host
