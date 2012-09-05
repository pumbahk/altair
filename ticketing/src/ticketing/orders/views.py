# -*- coding: utf-8 -*-

import csv
import itertools
from datetime import datetime

from pyramid import testing
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.url import route_path
from ticketing.cart.plugins.sej import DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID_SEJ
import webhelpers.paginate as paginate

from ticketing.models import merge_session_with_post, record_to_appstruct, merge_and_flush, record_to_multidict
from ticketing.operators.models import Operator, OperatorRole, Permission
from ticketing.core.models import Order, TicketPrintQueueEntry, Event, Performance
from ticketing.orders.export import OrderCSV
from ticketing.orders.forms import (OrderForm, OrderSearchForm, PerformanceSearchForm, SejOrderForm, SejTicketForm, SejTicketForm,
                                    SejRefundEventForm,SejRefundOrderForm)
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.orders.events import notify_order_canceled
from ticketing.tickets.utils import build_dicts_from_ordered_product_item

import pystache

@view_defaults(xhr=True) ## todo:適切な位置に移動
class OrdersAPIView(BaseView):
    @view_config(renderer="json", route_name="orders.api.performances")
    def get_performances(self):
        form_search = PerformanceSearchForm(self.request.params)
        if not form_search.validate():
            return {"result": [],  "status": False}

        query = Performance.query.filter(Performance.deleted_at == None)
        query = Performance.set_search_condition(query, form_search)
        performances = itertools.chain(query, [testing.DummyResource(id="", name="")])
        performances = [dict(pk=p.id, name=p.name) for p in performances]
        return {"result": performances, "status": True}
    
    @view_config(renderer="json", route_name="orders.api.printstatus", request_method="POST", match_param="action=save")
    def save_printstatus(self):
        """ [o:1, o:2, o:3, o:4, ....]
        """
        ords = [o.lstrip("o:") for o in self.request.POST.getall("targets[]") if o.startswith("o:")]
        ords = Order.query.filter(Order.id.in_(ords))

        orders = self.request.session.get("orders") or set()

        for o in ords:
            orders.add("o:%s" % o.id)
        self.request.session["orders"] = orders
        return {"status": True, "count": len(orders), "result": list(orders)}

    @view_config(renderer="json", route_name="orders.api.printstatus", request_method="GET", match_param="action=load")
    def load_printstatus(self):
        if not "orders" in self.request.session:
            return {"status": False, "result": [], "count": 0};
        orders = self.request.session["orders"]
        return {"status": True, "result": list(orders), "count": len(orders)}

    @view_config(renderer="json", route_name="orders.api.printstatus", request_method="POST", match_param="action=reset")
    def reset_printstatus(self):
        self.request.session["orders"] = set()
        return {"status": True, "count": 0, "result": []}


@view_defaults(decorator=with_bootstrap)
class Orders(BaseView):

    @view_config(route_name='orders.index', renderer='ticketing:templates/orders/index.html')
    def index(self):
        organization_id = int(self.context.user.organization_id)
        query = Order.filter(Order.organization_id==organization_id)

        event_query = Event.filter_by(organization_id=organization_id)
        form_search = OrderSearchForm(self.request.params).configure(event_query)
        if form_search.validate():
            query = Order.set_search_condition(query, form_search)

        page = int(self.request.params.get('page', 0))
        orders = paginate.Page(
            query,
            page=page,
            items_per_page=20,
            item_count=query.count(), 
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':OrderForm(),
            'form_search':form_search,
            'orders':orders,
            "page": page, 
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
            notify_order_canceled(self.request, order)
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
        query = Order.filter(Order.organization_id==int(self.context.user.organization_id))

        form_search = OrderSearchForm(self.request.params)
        if form_search.validate():
            query = Order.set_search_condition(query, form_search)

        orders = query.all()

        headers = [
            ('Content-Type', 'application/octet-stream; charset=cp932'),
            ('Content-Disposition', 'attachment; filename=orders_{date}.csv'.format(date=datetime.now().strftime('%Y%m%d%H%M%S')))
        ]
        response = Response(headers=headers)

        order_csv = OrderCSV(orders)

        writer = csv.DictWriter(response, order_csv.header, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(order_csv.rows)

        return response

    @view_config(route_name='orders.print.queue')
    def order_print_queue(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.query.get(order_id)

        tickets = []
        for ordered_product in order.items:
            for ordered_product_item in ordered_product.ordered_product_items:
                bundle = ordered_product_item.product_item.ticket_bundle
                dicts = build_dicts_from_ordered_product_item(ordered_product_item)
                for index, (seat, dict_) in enumerate(dicts):
                    for ticket in bundle.tickets:
                        ticket_format = ticket.ticket_format
                        applicable = False
                        for delivery_method in ticket_format.delivery_methods:
                            if delivery_method.delivery_plugin_id != DELIVERY_PLUGIN_ID_SEJ:
                                applicable = True
                                break
                        if not applicable:
                            continue
                        TicketPrintQueueEntry.enqueue(
                            operator=self.context.user,
                            ticket=ticket,
                            data={ u'drawing': pystache.render(ticket.data['drawing'], dict_) },
                            summary=u'注文 %s - %s%s' % (
                                order.order_no,
                                ordered_product_item.product_item.name,
                                (u' (%d / %d枚目)' % (index + 1, len(dicts))
                                 if len(dicts) > 1 else u'')
                                ),
                            ordered_product_item=ordered_product_item,
                            seat=seat
                            )

        return HTTPFound(location=self.request.route_path('orders.show', order_id=order_id))

from ticketing.sej.models import SejOrder, SejTicket, SejTicketTemplateFile, SejRefundEvent, SejRefundTicket
from ticketing.sej.ticket import SejTicketDataXml
from ticketing.sej import payment
from ticketing.sej.payment import request_update_order, request_cancel_order
from ticketing.sej.resources import code_from_ticket_type, code_from_update_reason, code_from_payment_type
from ticketing.sej.exceptions import  SejServerError
from sqlalchemy import or_, and_

from pyramid.threadlocal import get_current_registry

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
class SejOrderInfoView(object):

    def __init__(self, request):

        settings = get_current_registry().settings
        self.sej_hostname = settings['sej.inticket_api_url']
        self.shop_id = settings['sej.shop_id']
        self.secret_key = settings['sej.api_key']

        self.request = request

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
                    ),
                    shop_id=self.shop_id,
                    secret_key=self.secret_key,
                    hostname=self.sej_hostname
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
                shop_id=self.shop_id,
                secret_key=self.secret_key,
                hostname=self.sej_hostname
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

'''
from ticketing.core.models import  TicketPrintHistory

@view_defaults(decorator=with_bootstrap, permission="event_editor", renderer="json")
class TicketPrintApi(BaseView):
    @view_config(route_name='orders.api.ticket', request_method="GET")
    def get_ticket(self):
        ''' '''
        order = Order.filter_by(id=self.request.matchdict["id"]).first()
        if not order:
            return HTTPNotFound()

        tickets = []
        for ordered_product in order.ordered_products:
            for ordered_product_item in ordered_product.ordered_product_items:
                ticket_bundle = ordered_product_item.product_item.ticket_bundle
                if ticket_bundle:
                    for ticket in ticket_bundle.tickets:
                        data = ticket.data
                        tickets.append(data)

        return dict(tickets = tickets)

    @view_config(route_name='orders.api.ticket', request_method="POST")
    def print_ticket(self):
        ''' '''
        order = Order.filter_by(id=self.request.matchdict["id"]).first()
        if not order:
            return HTTPNotFound()

        now = datetime.now()
        for ordered_product in order.ordered_products:
            for ordered_product_item in ordered_product.ordered_product_items:
                ticket_bundle = ordered_product_item.product_item.ticket_bundle
                if ticket_bundle:
                    seats = ordered_product_item.seats
                    for ticket in ticket_bundle.tickets:
                        for seat in seats:
                            c = TicketPrintHistory(
                                operator = self.context.user,
                                ordered_product_item = ordered_product_item,
                                seat=seat,
                                ticket_bundle = ticket_bundle)
                            c.save()

        return dict(result='ok')
'''
