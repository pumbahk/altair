# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path
import webhelpers.paginate as paginate

from ticketing.models import merge_session_with_post, record_to_appstruct, merge_and_flush
from ..core.models import Organization
from ticketing.operators.models import Operator, OperatorRole, Permission
from ticketing.orders.models import Order
from ticketing.orders.forms import OrderForm
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

@view_defaults(decorator=with_bootstrap)
class Orders(BaseView):

    @view_config(route_name='orders.index', renderer='ticketing:templates/orders/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'Order.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Order.filter(Order.organization_id==int(self.context.user.organization_id))
        query = query.order_by(sort + ' ' + direction)

        # search condition
        if self.request.method == 'POST':
            condition = self.request.POST.get('order_number')
            if condition:
                query = query.filter(Order.id==condition)
            condition = self.request.POST.get('order_datetime_from')
            if condition:
                query = query.filter(Order.created_at>=condition)
            condition = self.request.POST.get('order_datetime_to')
            if condition:
                query = query.filter(Order.created_at<=condition)

        orders = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':OrderForm(),
            'orders':orders,
        }

    @view_config(route_name='orders.show', renderer='ticketing:templates/orders/show.html')
    def show(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        return {
            'order':order,
        }

from ticketing.sej.models import SejOrder
from ticketing.sej.payment import request_sej_exchange_sheet

@view_defaults(decorator=with_bootstrap)
class SejAdmin(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='orders.sej', renderer='ticketing:templates/sej/index.html')
    def index_get(self):
        sort = self.request.GET.get('sort', 'SejOrder.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = SejOrder.filter().order_by(sort + ' ' + direction)

        orders = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'orders': orders
        }


    @view_config(route_name='orders.sej.request', renderer='ticketing:templates/sej/request.html')
    def request_get(self):
        return {}
