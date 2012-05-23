# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path
import webhelpers.paginate as paginate

from ticketing.models import merge_session_with_post, record_to_appstruct, merge_and_flush
from ticketing.organizations.models import Organization
from ticketing.operators.models import Operator, OperatorRole, Permission
from ticketing.orders.models import Order
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

        orders = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
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
