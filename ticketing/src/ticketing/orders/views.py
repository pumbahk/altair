# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path
import webhelpers.paginate as paginate

from ticketing.models import merge_session_with_post, record_to_appstruct, merge_and_flush, record_to_multidict
from ..core.models import Organization
from ticketing.operators.models import Operator, OperatorRole, Permission
from ticketing.orders.models import Order
from ticketing.orders.forms import OrderForm, SejOrderForm
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

from ticketing.sej.models import SejOrder, SejTicketTemplateFile
from ticketing.sej.payment import SejTicketDataXml,request_sej_exchange_sheet, request_update_order
from ticketing.sej.resources import code_from_ticket_type, code_from_update_reason, code_from_payment_type

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

    @view_config(route_name='orders.sej.order.request', request_method="GET", renderer='ticketing:templates/sej/request.html')
    def order_request_get(self):
        f = SejOrderForm()
        templates = SejTicketTemplateFile.query.all()
        return dict(
            form=f,
            templates=templates
        )

    @view_config(route_name='orders.sej.order.request', request_method="POST", renderer='ticketing:templates/sej/request.html')
    def order_request_post(self):
        f = SejOrderForm(self.request.POST)
        templates = SejTicketTemplateFile.query.all()
        if f.validate():
            return HTTPFound(location=route_path('orders.sej'))
        else:
            return dict(
                form=f,
                templates=templates
            )

    @view_config(route_name='orders.sej.order.update', request_method="GET", renderer='ticketing:templates/sej/order_update.html')
    def order_update_get(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = SejOrder.query.get(order_id)


        templates = SejTicketTemplateFile.query.all()
        f = SejOrderForm(order_id=order.order_id)
        f.process(record_to_multidict(order))

        return dict(order=order, form=f, templates=templates)


    @view_config(route_name='orders.sej.order.update', request_method="POST",  renderer='ticketing:templates/sej/order_update.html')
    def order_update_post(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = SejOrder.query.get(order_id)

        tickets = []
        for ticket in order.tickets:
            td = dict(
                idx = ticket.ticket_idx,
                ticket_type         = code_from_ticket_type[int(ticket.ticket_type)],
                event_name          = ticket.event_name,
                performance_name    = ticket.performance_name,
                ticket_template_id  = ticket.ticket_template_id,
                performance_datetime= ticket.performance_datetime,
                xml                 = SejTicketDataXml(ticket.ticket_data_xml)
            )
            tickets.append(td)

        templates = SejTicketTemplateFile.query.all()
        print self.request.POST
        f = SejOrderForm(self.request.POST, order_id=order.order_id)
        if f.validate():
            data = f.data
            print code_from_ticket_type[int(order.payment_type)]

            order = request_update_order(
                update_reason   = code_from_update_reason[int(data.get('update_reason'))],
                total           = int(data.get('total_price')),
                ticket_total    = int(data.get('ticket_price')),
                commission_fee  = int(data.get('commission_fee')),
                ticketing_fee   = int(data.get('ticketing_fee')),
                payment_type    = code_from_payment_type[int(order.payment_type)],
                payment_due_at  = data.get('payment_due_at'),
                ticketing_start_at = data.get('ticketing_start_at'),
                ticketing_due_at = data.get('ticketing_due_at'),
                regrant_number_due_at = data.get('regrant_number_due_at'),
                tickets = tickets,
                condition=dict(
                    order_id        = order.order_id,
                    billing_number  = order.billing_number,
                    exchange_number = order.exchange_number,
                )
            )
            return dict(order=order, form=f, templates=templates)


        return dict(order=order, form=f, templates=templates)


    @view_config(route_name='orders.sej.order.cancel', renderer='ticketing:templates/sej/order_update.html')
    def order_update_cancel(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = SejOrder.query.get(order_id)
        return dict(order=order)

    @view_config(route_name='orders.sej.order.ticket.preview', renderer='ticketing:templates/sej/order_update.html')
    def order_ticket_preview(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = SejOrder.query.get(order_id)
        return dict(order=order)

    def request_get(self):
        return {}
