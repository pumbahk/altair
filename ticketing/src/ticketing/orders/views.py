# -*- coding: utf-8 -*-

import os
import csv

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.url import route_path
import webhelpers.paginate as paginate
from sqlalchemy import or_, and_

from ticketing.models import merge_session_with_post, record_to_appstruct, merge_and_flush, record_to_multidict
from ticketing.core.models import PaymentMethod, DeliveryMethod
from ticketing.operators.models import Operator, OperatorRole, Permission
from ticketing.orders.models import Order
from ticketing.orders.forms import (OrderForm, OrderSearchForm, SejOrderForm, SejTicketForm, SejTicketForm,
                                    SejRefundEventForm,SejRefundOrderForm)
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

@view_defaults(decorator=with_bootstrap)
class Orders(BaseView):

    @view_config(route_name='orders.index', renderer='ticketing:templates/orders/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'Order.id')
        direction = self.request.GET.get('direction', 'desc')
        if direction not in ['asc', 'desc']:
            direction = 'desc'

        query = Order.filter(Order.organization_id==int(self.context.user.organization_id))
        query = query.order_by(sort + ' ' + direction)

        # search condition
        # ToDo: 処理を切り出す
        form_search = OrderSearchForm(self.request.POST)
        if self.request.method == 'POST':
            condition = form_search.order_no.data
            if condition:
                query = query.filter(Order.order_no==condition)
            condition = form_search.ordered_from.data
            if condition:
                query = query.filter(Order.created_at>=condition)
            condition = form_search.ordered_to.data
            if condition:
                query = query.filter(Order.created_at<=condition)
            condition = form_search.payment_method.data
            if condition:
                query = query.join(Order.payment_delivery_pair)
                query = query.join(PaymentMethod)
                query = query.filter(PaymentMethod.payment_plugin_id.in_(condition))
            condition = form_search.delivery_method.data
            if condition:
                query = query.join(Order.payment_delivery_pair)
                query = query.join(DeliveryMethod)
                query = query.filter(DeliveryMethod.delivery_plugin_id.in_(condition))
            condition = form_search.status.data
            if condition:
                status_cond = []
                if 'refunded' in condition:
                    status_cond.append(and_(Order.canceled_at!=None, Order.paid_at!=None))
                if 'canceled' in condition:
                    status_cond.append(and_(Order.canceled_at!=None, Order.paid_at==None))
                if 'delivered' in condition:
                    status_cond.append(and_(Order.canceled_at==None, Order.delivered_at!=None))
                if 'paid' in condition:
                    status_cond.append(and_(Order.canceled_at==None, Order.paid_at!=None, Order.delivered_at==None))
                if 'ordered' in condition:
                    status_cond.append(and_(Order.canceled_at==None, Order.paid_at==None, Order.delivered_at==None))
                if status_cond:
                    query = query.filter(or_(*status_cond))

        orders = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':OrderForm(),
            'form_search':form_search,
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

    @view_config(route_name='orders.cancel')
    def cancel(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        if order.cancel(self.request):
            self.request.session.flash(u'受注(%s)をキャンセルしました' % order.order_no)
        else:
            self.request.session.flash(u'受注(%s)をキャンセルできません' % order.order_no)
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.delivered')
    def delivered(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        if order.delivered():
            self.request.session.flash(u'受注(%s)を配送済みにしました' % order.order_no)
        else:
            self.request.session.flash(u'受注(%s)を配送済みにできません' % order.order_no)
        return HTTPFound(location=route_path('orders.show', self.request, order_id=order.id))

    @view_config(route_name='orders.download')
    def download(self):
        # ToDo: 検索条件指定の結果をセットする、また上限件数をチェックする
        # ToDo: 処理を切り出す
        orders = Order.filter(Order.organization_id==int(self.context.user.organization_id)).all()

        headers = [
            ('Content-Type', 'text/csv'),
            ('Content-Disposition', 'attachment; filename=orders.csv')
        ]
        response = Response(headers=headers)

        # csv header
        order_header = [
            'order_no',
            'status',  #
            'created_at',  #
            'paid_at',
            'delivered_at',
            'canceled_at',
            ]
        user_profile_header = [
            'last_name',
            'first_name',
            'last_name_kana',
            'first_name_kana',
            'nick_name',
            ]
        shipping_address_header = [
            'last_name',  #
            'first_name',  #
            'last_name_kana',  #
            'first_name_kana',  #
            'zip',
            'country',
            'prefecture',
            'city',
            'address_1',
            'address_2',
            'tel_1',
            'fax',
            ]
        payment_header = [
            'total_amount',
            'transaction_fee',
            'delivery_fee',
            'system_fee',
            ]
        other_header = [
            'payment',
            'delivery',
            'event',
            'venue',
            'start_on',
            ]
        product_header = [
            'name',
            'price',
            'quantity',
            ]
        field_names = order_header + user_profile_header + shipping_address_header + payment_header + other_header

        # csv data
        rows = []
        for order in orders:
            order_dict = record_to_multidict(order)
            order_list = [(column, order_dict.get(column)) for column in order_header]
            payment_list = [(column, order_dict.get(column)) for column in payment_header]

            user_profile_dict = record_to_multidict(order.user.user_profile)
            user_profile_list = [(column, user_profile_dict.get(column)) for column in user_profile_header]

            shipping_address_dict = record_to_multidict(order.shipping_address)
            shipping_address_list = [(column, shipping_address_dict.get(column)) for column in shipping_address_header]

            other_list = [
                ('payment', order.payment_delivery_pair.payment_method.name),
                ('delivery', order.payment_delivery_pair.delivery_method.name),
                ('event', order.ordered_products[0].product.event.title),
                ('venue', order.ordered_products[0].ordered_product_items[0].product_item.performance.start_on),
                ('start_on', order.ordered_products[0].ordered_product_items[0].product_item.performance.venue.name),
            ]

            product_list = []
            for i, ordered_product in enumerate(order.ordered_products):
                for column in product_header:
                    column_name = 'product_%s_%s' % (column, i)
                    if not column_name in field_names:
                        field_names.append(column_name)
                    if column == 'name':
                        product_list.append((column_name, ordered_product.product.name))
                    if column == 'price':
                        product_list.append((column_name, ordered_product.price))
                    if column == 'quantity':
                        product_list.append((column_name, ordered_product.quantity))

            row = dict(order_list + user_profile_list + shipping_address_list + payment_list + other_list + product_list)
            for key, value in row.items():
                if value:
                    if not isinstance(value, unicode):
                        value = unicode(value)
                    value = value.encode('utf-8')
                else:
                    value = ''
                row[key] = value
            rows.append(row)

        writer = csv.DictWriter(response, field_names, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

        return response


from ticketing.sej.models import SejOrder, SejTicket, SejTicketTemplateFile, SejRefundEvent, SejRefundTicket
from ticketing.sej.ticket import SejTicketDataXml
from ticketing.sej.payment import request_update_order, request_cancel_order
from ticketing.sej.resources import code_from_ticket_type, code_from_update_reason, code_from_payment_type
from ticketing.sej.exceptions import  SejServerError
from sqlalchemy import or_, and_

import sqlahelper
DBSession = sqlahelper.get_session()

@view_defaults(decorator=with_bootstrap)
class SejOrderView(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='orders.sej', renderer='ticketing:templates/sej/index.html')
    def index_get(self):
        sort = self.request.GET.get('sort', 'SejOrder.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        filter = None
        query_str = self.request.GET.get('q', None)
        if query_str:
           filter = or_(
               SejOrder.billing_number.like('%'+ query_str +'%'),
               SejOrder.exchange_number.like('%'+ query_str + '%'),
               SejOrder.order_id.like('%'+ query_str + '%'),
               SejOrder.user_name.like('%'+ query_str + '%'),
               SejOrder.user_name_kana.like('%'+ query_str + '%'),
               SejOrder.email.like('%'+ query_str + '%'),
           )
        else:
            query_str = ''

        query = SejOrder.filter(filter).order_by(sort + ' ' + direction)
        orders = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'q' : query_str,
            'orders': orders
        }

@view_defaults(decorator=with_bootstrap)
class SejOrderInfoView(BaseView):

    @view_config(route_name='orders.sej.order.request', request_method="GET", renderer='ticketing:templates/sej/request.html')
    def order_request_get(self):
        f = SejOrderForm()
        ft = SejTicketForm()
        templates = SejTicketTemplateFile.query.all()
        return dict(
            form=f,
            ticket_form=ft,
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

    @view_config(route_name='orders.sej.order.info', request_method="GET", renderer='ticketing:templates/sej/order_info.html')
    def order_info_get(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = SejOrder.query.get(order_id)

        templates = SejTicketTemplateFile.query.all()
        f = SejOrderForm(order_id=order.order_id)
        tf = SejTicketForm()
        rf = SejRefundOrderForm()
        f.process(record_to_multidict(order))

        return dict(order=order, form=f, refund_form=rf, ticket_form=tf,templates=templates)


    @view_config(route_name='orders.sej.order.info', request_method="POST",  renderer='ticketing:templates/sej/order_info.html')
    def order_info_post(self):
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

        f = SejOrderForm(self.request.POST, order_id=order.order_id)
        if f.validate():
            data = f.data
            try:
                request_update_order(
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
                self.request.session.flash(u'オーダー情報を送信しました。')
            except SejServerError, e:
                self.request.session.flash(u'オーダー情報を送信に失敗しました。 %s' % e)
        else:
            print f.errors
            self.request.session.flash(u'バリデーションエラー：更新出来ませんでした。')

        return HTTPFound(location=self.request.route_path('orders.sej.order.info', order_id=order_id))
    #
    @view_config(route_name='orders.sej.order.ticket.data', request_method="GET", renderer='json')
    def order_info_ticket_data(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        ticket_id = int(self.request.matchdict.get('ticket_id', 0))
        order = SejOrder.query.get(order_id)
        if order:
            ticket = SejTicket.query.get(ticket_id)
            return dict(
                ticket_type = ticket.ticket_type,
                event_name = ticket.event_name,
                performance_name = ticket.performance_name,
                performance_datetime = ticket.performance_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                ticket_template_id = ticket.ticket_template_id,
                ticket_data_xml = ticket.ticket_data_xml,
            )
        return dict()

    @view_config(route_name='orders.sej.order.ticket.data', request_method="POST", renderer='ticketing:templates/sej/order_info.html')
    def order_info_ticket_data_post(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        ticket_id = int(self.request.matchdict.get('ticket_id', 0))
        order = SejOrder.query.get(order_id)
        if order:
            ticket = SejTicket.query.get(ticket_id)
            f = SejTicketForm(self.request.POST)
            print self.request.POST
            if f.validate():
                data = f.data
                ticket.event_name = data.get('event_name')
                ticket.performance_name = data.get('performance_name')
                ticket.performance_datetime = data.get('performance_datetime')
                ticket.ticket_template_id = data.get('ticket_template_id')
                ticket.ticket_data_xml = data.get('ticket_data_xml')
                self.request.session.flash(u'チケット情報を更新しました。')
            else:
                self.request.session.flash(u'バリデーションエラー：更新出来ませんでした。')

        return HTTPFound(location=self.request.route_path('orders.sej.order.info', order_id=order_id))

    @view_config(route_name='orders.sej.order.cancel', renderer='ticketing:templates/sej/order_info.html')
    def order_cancel(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = SejOrder.query.get(order_id)

        try:
            order = request_cancel_order(
                order.order_id,
                order.billing_number,
                order.exchange_number,
            )
            self.request.session.flash(u'オーダーをキャンセルしました。')
        except SejServerError, e:
            self.request.session.flash(u'オーダーをキャンセルに失敗しました。 %s' % e)

        return HTTPFound(location=self.request.route_path('orders.sej.order.info', order_id=order_id))

@view_defaults(decorator=with_bootstrap)
class SejRefundView(BaseView):

    @view_config(route_name='orders.sej.event.refund', renderer='ticketing:templates/sej/event_refund.html')
    def order_event_refund(self):

        sort = self.request.GET.get('sort', 'SejRefundEvent.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = SejRefundEvent.filter().order_by(sort + ' ' + direction)

        events = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        f = SejRefundEventForm()
        return dict(
            form = f,
            events = events
        )

    @view_config(route_name='orders.sej.event.refund.detail', renderer='ticketing:templates/sej/event_refund_detail.html')
    def order_event_detail(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = SejRefundEvent.query.get(event_id)
        return dict(event=event)

    @view_config(route_name='orders.sej.event.refund.add', renderer='ticketing:templates/sej/event_form.html')
    def order_event_refund_add(self):
        f = SejRefundEventForm(self.request.POST)
        if f.validate():
            e = SejRefundEvent()
            d = f.data
            e.available = d.get('available')
            e.shop_id = d.get('shop_id')
            e.event_code_01 = d.get('event_code_01')
            e.event_code_02 = d.get('event_code_02')
            e.title = d.get('title')
            e.sub_title = d.get('sub_title')
            e.event_at = d.get('event_at')
            e.start_at = d.get('start_at')
            e.end_at = d.get('end_at')
            e.ticket_expire_at = d.get('ticket_expire_at')
            e.event_expire_at = d.get('event_expire_at')
            e.refund_enabled = d.get('refund_enabled')
            e.disapproval_reason = d.get('disapproval_reason')
            e.need_stub = d.get('need_stub')
            e.remarks = d.get('remarks')
            DBSession.add(e)
        else:
            return dict(
                form = f
            )

        return HTTPFound(location=self.request.route_path('orders.sej.event.refund'))

    @view_config(route_name='orders.sej.order.ticket.refund', request_method='POST', renderer='ticketing:templates/sej/ticket_refund.html')
    def order_ticket_refund(self):

        ticket_id = int(self.request.matchdict.get('ticket_id', 0))
        ticket = SejTicket.query.get(ticket_id)

        f = SejRefundOrderForm(self.request.POST)
        if f.validate():
            data = f.data
            event = data.get('event')
            from sqlalchemy.orm.exc import NoResultFound
            try:
                ct = SejRefundTicket.filter(
                    and_(
                        SejRefundTicket.order_id == ticket.ticket.order_id,
                        SejRefundTicket.ticket_barcode_number == ticket.barcode_number
                    )).one()
            except NoResultFound, e:
                ct = SejRefundTicket()
                DBSession.add(ct)
            print event

            ct.available     = 1
            ct.event_code_01 = event.event_code_01
            ct.event_code_02 = event.event_code_02
            ct.order_id = ticket.ticket.order_id
            ct.ticket_barcode_number = ticket.barcode_number
            ct.refund_ticket_amount = data.get('refund_ticket_amount')
            ct.refund_other_amount = data.get('refund_other_amount')
            event.tickets.append(ct)
            DBSession.flush()

            self.request.session.flash(u'払い戻し予約を行いました。')
        else:
            self.request.session.flash(u'失敗しました')

        return HTTPFound(location=self.request.route_path('orders.sej.order.info', order_id=ticket.ticket.id))

# @TODO move this
@view_defaults(decorator=with_bootstrap)
class SejTicketTemplate(BaseView):

    @view_config(route_name='orders.sej.ticket_template', renderer='ticketing:templates/sej/ticket_template.html')
    def order_ticket_preview(self):

        sort = self.request.GET.get('sort', 'SejTicketTemplateFile.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'


        query = SejTicketTemplateFile.filter().order_by(sort + ' ' + direction)

        templates = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return dict(
            templates=templates
        )


