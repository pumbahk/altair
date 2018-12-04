# -*- coding:utf-8 -*-

import logging
from datetime import datetime, timedelta

from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentSetting
from altair.app.ticketing.orders.models import Order, Performance
from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_DELIVERY_PLUGIN_ID
from altair.app.ticketing.payments.plugins.models import ReservedNumber
from altair.app.ticketing.users.models import Membership
from altair.sqlahelper import get_db_session
from pyramid.decorator import reify
from altair.app.ticketing.resources import TicketingAdminResource

from .searcher import SalesSearcher
from altair.app.ticketing.operators.models import Operator

logger = logging.getLogger(__name__)


class SalesSearchResource(TicketingAdminResource):
    def __init__(self, request):
        super(SalesSearchResource, self).__init__(request)

        if not self.user:
            return

        self.request = request
        self.session = get_db_session(request, 'slave')
        self.searcher = SalesSearcher(get_db_session(request, name="slave"))

    def search(self, sales_search_form):
        return self.searcher.search(
            self.organization.id,
            sales_search_form.sales_kind.data,
            sales_search_form.sales_term.data,
            sales_search_form.salessegment_group_kind.data,
            sales_search_form.operators.data
        )

    def get_sales_report_operators(self):
        operators = self.session.query(Operator)\
            .filter(Operator.organization_id == self.organization.id)\
            .filter(Operator.sales_search==True)\
            .with_entities(Operator.id, Operator.name)\
            .all()
        return operators
