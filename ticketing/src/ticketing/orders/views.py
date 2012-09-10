# -*- coding: utf-8 -*-

import json
import logging
import csv
import itertools
from datetime import datetime

from pyramid import testing
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from ticketing.cart.plugins.sej import DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID_SEJ
from paste.util.multidict import MultiDict
import webhelpers.paginate as paginate
from wtforms import ValidationError
from wtforms.validators import Optional

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.operators.models import Operator, OperatorRole, Permission
from ticketing.core.models import Order, TicketPrintQueueEntry, Event, Performance, Product, PaymentDeliveryMethodPair, ShippingAddress, OrderedProductItem, Ticket, TicketBundle, ProductItem, OrderedProduct, TicketFormat, Ticket_TicketBundle
from ticketing.users.models import MailSubscription
from ticketing.orders.export import OrderCSV
from ticketing.orders.forms import (OrderForm, OrderSearchForm, SejOrderForm, SejTicketForm, 
                                    SejRefundEventForm,SejRefundOrderForm, SendingMailForm, 
                                    PerformanceSearchForm, OrderReserveForm,
                                    PreviewTicketSelectForm, CheckedOrderTicketChoiceForm)
from lxml import etree
from ticketing.tickets.convert import to_opcodes
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.orders.events import notify_order_canceled
from ticketing.tickets.utils import build_dicts_from_ordered_product_item
from ticketing.cart import api
from ticketing.cart.schemas import ClientForm

logger = logging.getLogger(__name__)
import pystache
from . import utils

logger = logging.getLogger(__name__)

def available_ticket_formats_for_orders(orders):
    return TicketFormat.query\
        .filter(TicketFormat.id==Ticket.ticket_format_id)\
        .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
        .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
        .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
        .filter(ProductItem.id==OrderedProductItem.product_item_id)\
        .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
        .filter(OrderedProduct.order_id.in_(orders))\
        .with_entities(TicketFormat.id, TicketFormat.name)\
        .distinct(TicketFormat.id)

def available_ticket_formats_for_ordered_product_item(ordered_product_item_id):
    return TicketFormat.query\
        .filter(TicketFormat.id==Ticket.ticket_format_id)\
        .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
        .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
        .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
        .filter(ProductItem.id==OrderedProductItem.product_item_id)\
        .filter(OrderedProductItem.id==ordered_product_item_id)\
        .with_entities(TicketFormat.id, TicketFormat.name)\
        .distinct(TicketFormat.id)

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


    @view_config(renderer="json", route_name="orders.api.printstatus", request_method="POST", match_param="action=add")
    def add_printstatus(self):
        """ [o:1, o:2, o:3, o:4, ....]
        """
        oid = self.request.POST["target"]
        if not oid.startswith("o:"):
            return {"status": False}
        # order = Order.query.filter(Order.id==oid.lstrip("o:")).first()
        # if not order:
        #     return {"status": False}

        orders = self.request.session.get("orders") or set()
        orders.add(oid)
        self.request.session["orders"] = orders
        return {"status": True, "count": len(orders), "result": list(orders)}

    @view_config(renderer="json", route_name="orders.api.printstatus", request_method="POST", match_param="action=remove")
    def remove_printstatus(self):
        """ [o:1, o:2, o:3, o:4, ....]
        """
        oid = self.request.POST["target"]
        if not oid.startswith("o:"):
            return {"status": False}
        # order = Order.query.filter(Order.id==oid.lstrip("o:")).first()
        # if not order:
        #     return {"status": False}
        
        orders = self.request.session.get("orders") or set()
        orders.remove(oid)
        self.request.session["orders"] = orders
        return {"status": True, "count": len(orders), "result": list(orders)}

    @view_config(renderer="json", route_name="orders.api.printstatus", request_method="GET", match_param="action=load")
    def load_printstatus(self):
        if not "orders" in self.request.session:
            return {"status": False, "result": [], "count": 0}
        orders = self.request.session["orders"]
        return {"status": True, "result": list(orders), "count": len(orders)}

    @view_config(renderer="json", route_name="orders.api.printstatus", request_method="POST", match_param="action=reset")
    def reset_printstatus(self):
        self.request.session["orders"] = set()
        return {"status": True, "count": 0, "result": []}


    @view_config(renderer="json", route_name="orders.api.orders", request_method="GET", match_param="action=matched_by_ticket", 
                 request_param="ticket_format_id")
    def checked_matched_orders(self):
        if not "orders" in self.request.session:
            return {"status": False, "result": []}
        ticket_format_id = self.request.GET["ticket_format_id"]
        exclude_issued = self.request.GET.get("exclude_issued", False)
        ords = self.request.session["orders"]
        ords = [o.lstrip("o:") for o in ords if o.startswith("o:")]
        qs = Order.query\
            .filter(Order.deleted_at==None).filter(Order.id.in_(ords))\
            .filter(OrderedProduct.order_id.in_(ords))\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(ProductItem.id==OrderedProductItem.product_item_id)\
            .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
            .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
            .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
            .filter(Ticket.ticket_format_id==ticket_format_id).distinct()
        if exclude_issued:
            qs = qs.filter(Order.issued==False)

        orders_list = [dict(order_no=o.order_no, event_name=o.performance.event.title, total_amount=int(o.total_amount)) 
                       for o in qs]
        return {"results": orders_list, "status": True}

def session_has_order_p(context, request):
    return bool(request.session.get("orders"))

@view_defaults(decorator=with_bootstrap)
class Orders(BaseView):
    @view_config(route_name="orders.checked.queue.dialog", renderer="ticketing:templates/orders/_checked_queue_dialog.html", 
                 custom_predicates=(session_has_order_p,))
    def checked_queue_dialog(self):
        ords = self.request.session["orders"]
        ords = [o.lstrip("o:") for o in ords if o.startswith("o:")]
        form = CheckedOrderTicketChoiceForm(ticket_formats=available_ticket_formats_for_orders(ords))
        return {"form": form}

    @view_config(route_name="orders.checked.queue.dialog", renderer="string")
    def checked_queue_dialog_error(self):
        params = dict(header=u"エラー", body=u"チェックした注文はありません")
        return u"""
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal">×</button>
    %(header)s
  </div>
  <div class="modal-body">
    %(body)s
  </div>
  <div class="modal-footer">
	<a href="#" class="btn" data-dismiss="modal">キャンセル</a>
  </div>
""" % params
        
    @view_config(route_name="orders.checked.index", renderer='ticketing:templates/orders/index.html')
    def checked_orders_index(self):
        """後でindexと合成。これはチェックされたOrderだけを表示するview
        """
        if not self.request.session["orders"]:
            return HTTPFound(self.request.route_url("orders.index"))

        organization_id = int(self.context.user.organization_id)
        query = Order.filter(Order.organization_id==organization_id)
        ords = [o.lstrip("o:") for o in self.request.session["orders"] if o.startswith("o:")]
        query = query.filter(Order.id.in_(ords))

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

        if order.shipping_address:
            mail_magazines = [ms.segment.name for ms in MailSubscription.query.filter_by(email=order.shipping_address.email).all()]
            form_shipping_address = ClientForm(record_to_multidict(order.shipping_address))
            form_shipping_address.tel.data = order.shipping_address.tel_1
            form_shipping_address.mail_address.data = order.shipping_address.email
        else:
            mail_magazines = []
            form_shipping_address = ClientForm()

        form_order = OrderForm(record_to_multidict(order))

        return {
            'order':order,
            'mail_magazines':mail_magazines,
            'form_shipping_address':form_shipping_address,
            'form_order':form_order,
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

    @view_config(route_name='orders.reserve.form', request_method='POST', renderer='ticketing:templates/orders/_form_reserve.html')
    def reserve_form(self):
        post_data = MultiDict(self.request.json_body)
        logger.debug('order reserve post_data=%s' % post_data)

        performance_id = int(post_data.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            logger.error('performance id %d is not found' % performance_id)
            return HTTPBadRequest(body=json.dumps({
                'message':u'パフォーマンスが存在しません',
            }))

        # Stockとkind=vipのSalesSegmentからProductを決定する
        stocks = post_data.get('stocks')
        form_reserve = OrderReserveForm(post_data, performance_id=performance_id, stocks=stocks)
        form_reserve.product_id.validators = [Optional()]
        form_reserve.payment_delivery_method_pair_id.validators = [Optional()]
        form_reserve.validate()

        return {'form':form_reserve}

    @view_config(route_name='orders.reserve', request_method='POST', renderer='json')
    def reserve(self):
        post_data = MultiDict(self.request.json_body)
        logger.debug('order reserve post_data=%s' % post_data)

        performance_id = int(post_data.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            logger.error('performance id %d is not found' % performance_id)
            return HTTPBadRequest(body=json.dumps({
                'message':u'パフォーマンスが存在しません',
            }))

        try:
            # validation
            f = OrderReserveForm(performance_id=performance_id, stocks=post_data.get('stocks'))
            print post_data
            f.process(post_data)
            if not f.validate():
                raise ValidationError(reduce(lambda a,b: a+b, f.errors.values(), []))

            product = DBSession.query(Product).filter_by(id=post_data.get('product_id')).one()
            seats = post_data.get('seats')
            if product.seat_stock_type.quantity_only:
                quantity = int(post_data.get('quantity') or 0)
            else:
                quantity = len(seats)
                if quantity == 0:
                    raise ValidationError(u'座席が選択されていません')

            # create cart
            order_items = [(product, quantity)]
            cart = api.order_products(self.request, performance_id, order_items, selected_seats=seats)
            pdmp = DBSession.query(PaymentDeliveryMethodPair).filter_by(id=post_data.get('payment_delivery_method_pair_id')).one()
            cart.payment_delivery_pair = pdmp
            cart.system_fee = pdmp.system_fee
            DBSession.add(cart)
            DBSession.flush()

            # create order
            order = Order.create_from_cart(cart)
            order.organization_id = order.performance.event.organization_id
            order.note = post_data.get('note')
            DBSession.add(order)
            DBSession.flush()
            cart.finish()

            self.request.session.flash(u'予約しました')
            return {'order_id':order.id}
        except ValidationError, e:
            logger.exception('validation error (%s)' % e.message)
            return HTTPBadRequest(body=json.dumps({
                'message':e.message,
            }))

        except Exception, e:
            logger.exception('save error (%s)' % e.message)
            return HTTPBadRequest(body=json.dumps({
                'message':u'エラーが発生しました',
            }))

    @view_config(route_name='orders.edit.shipping_address', request_method='POST', renderer='ticketing:templates/orders/_form_shipping_address.html')
    def edit_shipping_address_post(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        f = ClientForm(self.request.POST)
        # ここでは確認用メールアドレスはチェック対象外
        f.mail_address2.data = self.request.POST.get('mail_address')

        if f.validate():
            shipping_address = merge_session_with_post(order.shipping_address or ShippingAddress(), f.data)
            shipping_address.tel_1 = f.tel.data
            shipping_address.email = f.mail_address.data
            order.shipping_address = shipping_address
            order.save()

            self.request.session.flash(u'予約を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='orders.edit.product', request_method='POST', renderer='ticketing:templates/orders/_form_product.html')
    def edit_product_post(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id)
        if order is None:
            return HTTPNotFound('order id %d is not found' % order_id)

        f = OrderForm(self.request.POST)

        try:
            if not f.validate():
                raise ValidationError()

            order.system_fee = f.system_fee.data
            order.transaction_fee = f.transaction_fee.data
            order.delivery_fee = f.delivery_fee.data

            for op in order.items:
                op.price = int(self.request.params.get('product_price-%d' % op.id) or 0)
                # 個数が変更できるのは数受けのケースのみ
                if op.product.seat_stock_type.quantity_only:
                    op.quantity = int(self.request.params.get('product_quantity-%d' % op.id) or 0)
                for opi in op.ordered_product_items:
                    opi.price = int(self.request.params.get('product_item_price-%d' % opi.id) or 0)
                if sum(opi.price for opi in op.ordered_product_items) != op.price:
                    raise ValidationError(u'小計金額が正しくありません')

            total_amount = sum(op.price * op.quantity for op in order.items)\
                           + order.system_fee + order.transaction_fee + order.delivery_fee
            if order.status in ('paid', 'delivered'):
                if total_amount != order.total_amount:
                    raise ValidationError(u'入金済みの為、合計金額は変更できません')
            order.total_amount = total_amount

            order.save()
        except ValidationError, e:
            if e.message:
                self.request.session.flash(e.message)
            return {'form':f, 'order':order}
        except Exception, e:
            logger.exception('save error (%s)' % e.message)
            self.request.session.flash(u'入力された金額および個数が不正です')
            return {'form':f, 'order':order}

        self.request.session.flash(u'予約を保存しました')
        return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name='orders.note', request_method='POST', renderer='json')
    def note(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id)
        if order is None:
            return HTTPBadRequest(body=json.dumps({
                'message':u'不正なデータです',
            }))

        f = OrderReserveForm(MultiDict(self.request.json_body))
        if not f.note.validate(f):
            logger.debug('validation error (%s)' % f.note.errors)
            return HTTPBadRequest(body=json.dumps({
                'message':f.note.errors,
            }))

        order.note = f.note.data
        order.save()
        return {}

    @view_config(route_name="orders.item.preview", request_method="GET", 
                 renderer='ticketing:templates/orders/_item_preview_dialog.html'
                 )
    def order_item_preview_dialog(self):
        item = OrderedProductItem.query.filter_by(id=self.request.matchdict["item_id"]).first()
        if item is None:
            return {} ### xxx:
        form = PreviewTicketSelectForm(item_id=item.id, ticket_formats=available_ticket_formats_for_ordered_product_item(item.id))
        return {"form": form, "item": item}

    @view_config(route_name="orders.item.preview.getdata", request_method="GET", 
                 renderer="json")
    def order_item_get_data_for_preview(self):
        item = OrderedProductItem.query.filter_by(id=self.request.matchdict["item_id"]).one()
        ticket_format = TicketFormat.query.filter_by(id=self.request.matchdict["ticket_format_id"]).one()
        tickets = Ticket.query \
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(ProductItem.id==OrderedProductItem.product_item_id)\
            .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
            .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
            .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
            .filter(Ticket.ticket_format_id==ticket_format.id)\
            .filter(OrderedProductItem.id==item.id)\
            .all()
        dicts = build_dicts_from_ordered_product_item(item)
        data = dict(ticket_format.data)
        results = []
        names = []
        for seat, dict_ in dicts:
            names.append(seat.name)
            for ticket in tickets:
                svg = pystache.render(ticket.data['drawing'], dict_)
                r = data.copy()
                r.update(dict(drawing=' '.join(to_opcodes(etree.ElementTree(etree.fromstring(svg))))))
                results.append(r)
        return {"results": results, "names": names}

    @view_config(route_name="orders.issue_status", request_method="POST", \
                 request_param='issued')
    def issue_status(self):
        order = Order.query.get(self.request.matchdict["order_id"])
        order.issued = int(self.request.params['issued'])
        return HTTPFound(location=self.request.route_path('orders.show', order_id=order.id))

    @view_config(route_name="orders.print.queue.dialog", request_method="GET", 
                 renderer="ticketing:templates/orders/_print_queue_dialog.html")
    def print_queue_dialog(self):
        order = Order.query.get(self.request.matchdict["order_id"])
        form = CheckedOrderTicketChoiceForm(ticket_formats=available_ticket_formats_for_orders([order.id]))
        return {"form": form, "order": order}

    @view_config(route_name="orders.print.queue.manymany", request_method="POST", 
                 request_param="ticket_format_id")
    def order_print_queue_manymany(self):
        ticket_format_id = self.request.POST["ticket_format_id"]
        ticket_format = TicketFormat.query.filter_by(id=ticket_format_id).first()
        if ticket_format is None:
            raise HTTPFound(location=self.request.route_path('orders.index'))

        ords = self.request.session["orders"]
        ords = [o.lstrip("o:") for o in ords if o.startswith("o:")]

        qs = DBSession.query(Order)\
            .filter(Order.deleted_at==None).filter(Order.id.in_(ords))\
            .filter(Order.issued==False)\
            .filter(OrderedProduct.order_id.in_(ords))\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(ProductItem.id==OrderedProductItem.product_item_id)\
            .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
            .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
            .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
            .filter(TicketFormat.id==ticket_format_id) \
            .distinct()

        for order in qs:
            utils.enqueue_for_order(operator=self.context.user, order=order, ticket_format=ticket_format)

        # def clean_session_callback(request):
        logger.info("*ticketing print queue many* clean session")
        session_values = self.request.session["orders"]
        for order in qs:
            session_values.remove("o:%s" % order.id)
        self.request.session["orders"] = session_values
        # self.request.add_finished_callback(clean_session_callback)

        self.request.session.flash(u'券面を印刷キューに追加しました')
        return HTTPFound(location=self.request.route_path('orders.index'))
        
    @view_config(route_name="orders.print.queue.strict", request_method="POST")
    def order_print_queue_strict(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.query.get(order_id)

        form = CheckedOrderTicketChoiceForm(formdata=self.request.POST, ticket_formats=available_ticket_formats_for_orders([order.id]))
        if not form.validate():
            self.request.session.flash(u'失敗: %s' % form.errors)
            return HTTPFound(location=self.request.route_path('orders.show', order_id=order_id))

        utils.enqueue_for_order(
            operator=self.context.user,
            order=order,
            ticket_format=TicketFormat.query.filter_by(id=form.data['ticket_format_id']).one()
            )
        self.request.session.flash(u'券面を印刷キューに追加しました')
        return HTTPFound(location=self.request.route_path('orders.show', order_id=order_id))


    @view_config(route_name='orders.print.queue')
    def order_print_queue(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.query.get(order_id)
        utils.enqueue_for_order(operator=self.context.user, order=order)
        self.request.session.flash(u'券面を印刷キューに追加しました')
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

import ticketing.mails.complete as mails_complete
import ticketing.mails.order_cancel as mails_cancel
@view_defaults(decorator=with_bootstrap, permission="authenticated", route_name="orders.mailinfo")
class MailInfoView(BaseView):
    @view_config(match_param="action=show", renderer="ticketing:templates/orders/mailinfo/show.html")
    def show(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id)
        message = mails_complete.build_message(self.request, order)
        mail_form = SendingMailForm(subject=message.subject, 
                                    recipient=message.recipients[0], 
                                    bcc=message.bcc[0] if message.bcc else "")
        performance = order.performance
        return dict(order=order, mail_form=mail_form, performance=performance)

    @view_config(match_param="action=complete_mail_preview", renderer="string")
    def complete_mail_preview(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id)
        return mails_complete.preview_text(self.request, order)

    @view_config(match_param="action=complete_mail_send", renderer="string", request_method="POST")
    def complete_mail_send(self):
        form = SendingMailForm(self.request.POST)
        order_id = int(self.request.matchdict.get('order_id', 0))
        if not form.validate():
            self.request.session.flash(u'失敗しました: %s' % form.errors)
            raise HTTPFound(self.request.current_route_url(order_id=order_id, action="show"))

        order = Order.get(order_id)
        mails_complete.send_mail(self.request, order, override=form.data)
        self.request.session.flash(u'メール再送信しました')
        return HTTPFound(self.request.current_route_url(order_id=order_id, action="show"))

    @view_config(match_param="action=cancel_mail_preview", renderer="string")
    def cancel_mail_preview(self):
        order_id = int(self.request.matchdict.get('order_id', 0))
        order = Order.get(order_id)
        return mails_cancel.preview_text(self.request, order)

    @view_config(match_param="action=cancel_mail_send", renderer="string", request_method="POST")
    def cancel_mail_send(self):
        form = SendingMailForm(self.request.POST)
        order_id = int(self.request.matchdict.get('order_id', 0))
        if not form.validate():
            self.request.session.flash(u'失敗しました: %s' % form.errors)
            raise HTTPFound(self.request.current_route_url(order_id=order_id, action="show"))

        order = Order.get(order_id)
        mails_cancel.send_mail(self.request, order, override=form.data)
        self.request.session.flash(u'メール再送信しました')
        return HTTPFound(self.request.current_route_url(order_id=order_id, action="show"))

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
