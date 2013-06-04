# -*- coding:utf-8 -*-
import logging
import re
import json
import transaction
from datetime import datetime
#from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from markupsafe import Markup

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid.threadlocal import get_current_request
from pyramid import security
from webob.multidict import MultiDict

from altair.pyramid_boto.s3.assets import IS3KeyProvider

from ticketing.models import DBSession
from ticketing.core import models as c_models
from ticketing.core import api as c_api
from ticketing.mailmags.api import get_magazines_to_subscribe, multi_subscribe
from ticketing.views import mobile_request
from ticketing.fanstatic import with_jquery, with_jquery_tools
from ticketing.payments.payment import Payment
from ticketing.payments.exceptions import PaymentDeliveryMethodPairNotFound
from ticketing.users.api import get_or_create_user
from ticketing.venues.api import get_venue_site_adapter
from altair.mobile.interfaces import IMobileRequest

from . import api
from . import helpers as h
from . import schemas
from .events import notify_order_completed
from .reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from .stocker import InvalidProductSelectionException, NotEnoughStockException
from .selectable_renderer import selectable_renderer
from .api import get_seat_type_triplets
from .view_support import IndexViewMixin, get_amount_without_pdmp
from .exceptions import (
    NoCartError, 
    NoPerformanceError,
    InvalidCSRFTokenException, 
    CartCreationException,
)

logger = logging.getLogger(__name__)


def back_to_product_list_for_mobile(request):
    cart = api.get_cart_safe(request)
    cart.release()
    api.remove_cart(request)
    return HTTPFound(
        request.route_url(
            route_name='cart.products',
            event_id=cart.performance.event_id,
            performance_id=cart.performance_id,
            sales_segment_id=cart.sales_segment_id,
            seat_type_id=cart.products[0].product.items[0].stock.stock_type_id))


def back_to_top(request):
    event_id = request.params.get('event_id')
    if event_id is None:
        cart = api.get_cart(request)
        if cart is not None:
            event_id = cart.performance.event_id
    ReleaseCartView(request)()
    return HTTPFound(event_id and request.route_url('cart.index', event_id=event_id) or '/')

def back(pc=back_to_top, mobile=None):
    if mobile is None:
        mobile = pc

    def factory(func):
        def retval(*args, **kwargs):
            request = get_current_request()
            if request.params.has_key('back'):
                if IMobileRequest.providedBy(request):
                    return mobile(request)
                else:
                    return pc(request)
            return func(*args, **kwargs)
        return retval
    return factory



@view_defaults(decorator=with_jquery.not_when(mobile_request))
class IndexView(IndexViewMixin):
    """ 座席選択画面 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

        self.prepare()

    def get_frontend_drawing_urls(self, venue):
        sales_segment = self.request.context.sales_segment
        retval = {}
        drawings = get_venue_site_adapter(self.request, venue.site).get_frontend_drawings()
        if drawings:
            for name, drawing in drawings.items():
                if IS3KeyProvider.providedBy(drawing):
                    key = drawing.get_key()
                    headers = {}
                    if re.match('^.+\.(svgz|gz)$', drawing.path):
                        headers['response-content-encoding'] = 'gzip'
                    url = key.generate_url(expires_in=1800, response_headers=headers)
                else:
                    url = self.request.route_url(
                        'cart.venue_drawing',
                        event_id=self.request.context.event_id,
                        performance_id=sales_segment.performance.id,
                        venue_id=sales_segment.performance.venue.id,
                        part=name)
                retval[name] = url
        return retval

    def is_smartphone(context, request):
        SMARTPHONE_USER_AGENT_RX = re.compile("iPhone|iPod|Opera Mini|Android.*Mobile|NetFront|PSP|BlackBerry")
        if "HTTP_USER_AGENT" in request.environ:
            if SMARTPHONE_USER_AGENT_RX.search(request.environ["HTTP_USER_AGENT"]):

                return True
        return False

    def is_organization_rs(context, request):
        organization = c_api.get_organization(request)
        return organization.id == 15

    @view_config(decorator=with_jquery_tools, route_name='cart.index',
                 custom_predicates=(is_smartphone,is_organization_rs), renderer=selectable_renderer("carts_smartphone/RT/index.html"), xhr=False, permission="buy")
    @view_config(decorator=with_jquery_tools, route_name='cart.index',
                  renderer=selectable_renderer("carts/%(membership)s/index.html"), xhr=False, permission="buy")
    def __call__(self):
        self.check_redirect(mobile=False)
        sales_segments = self.context.available_sales_segments
        selector_name = c_api.get_organization(self.request).setting.performance_selector

        performance_selector = api.get_performance_selector(self.request, selector_name)
        sales_segments_selection = performance_selector()
        logger.debug("sales_segments: %s" % sales_segments_selection)

        # 会場
        try:
            performance_id = long(self.request.params.get('pid') or self.request.params.get('performance'))
        except (ValueError, TypeError):
            performance_id = None

        selected_sales_segment = None
        if not performance_id:
            # GETパラメータ指定がなければ、選択肢の1つ目を採用
            selected_sales_segment = sales_segments[0]
        else:
            # パフォーマンスIDから販売区分の解決を試みる
            # performance_id で指定される Performance は
            # available_sales_segments に関連するものでなければならない

            # 数が少ないのでリニアサーチ
            for sales_segment in sales_segments:
                if sales_segment.performance.id == performance_id:
                    # 複数個の SalesSegment が該当する可能性があるが
                    # 最初の 1 つを採用することにする。実用上問題ない。
                    selected_sales_segment = sales_segment
                    break

            # performance_id が指定されていて、かつパフォーマンスが見つからない
            # 場合は例外
            if selected_sales_segment is None:
                raise NoPerformanceError(event_id=self.context.event.id)

        return dict(
            event=dict(
                id=self.context.event.id,
                code=self.context.event.code,
                title=self.context.event.title,
                abbreviated_title=self.context.event.abbreviated_title,
                sales_start_on=str(self.context.event.sales_start_on),
                sales_end_on=str(self.context.event.sales_end_on),
                venues=set(p.venue.name for p in self.context.event.performances),
                product=self.context.event.products
                ),
            dates=sorted(list(set([p.start_on.strftime("%Y-%m-%d %H:%M") for p in self.context.event.performances]))),
            cart_release_url=self.request.route_url('cart.release'),
            selected=Markup(
                json.dumps([
                    performance_selector.select_value(selected_sales_segment),
                    selected_sales_segment.id])),
            sales_segments_selection=Markup(json.dumps(sales_segments_selection)),
            event_extra_info=self.event_extra_info.get("event") or [],
            selection_label=performance_selector.label,
            second_selection_label=performance_selector.second_label,
            )

    @view_config(route_name='cart.seat_types', renderer="json")
    @view_config(route_name='cart.seat_types.obsolete', renderer="json")
    def get_seat_types(self):
        sales_segment = self.request.context.sales_segment # XXX: matchdict から取得していることを期待

        seat_type_triplets = get_seat_type_triplets(sales_segment.id)
        data = dict(
            seat_types=[
                dict(
                    id=s.id,
                    name=s.name,
                    description=s.description,
                    style=s.style,
                    products_url=self.request.route_url('cart.products',
                        event_id=self.request.context.event_id,
                        performance_id=sales_segment.performance.id,
                        sales_segment_id=sales_segment.id,
                        seat_type_id=s.id),
                    availability=available > 0,
                    availability_text=h.get_availability_text(available),
                    quantity_only=s.quantity_only,
                    seat_choice=sales_segment.seat_choice
                    )
                for s, total, available in seat_type_triplets
                ],
            event_name=sales_segment.performance.event.title,
            performance_name=sales_segment.performance.name,
            performance_start=h.performance_date(sales_segment.performance),
            performance_id=sales_segment.performance.id,
            sales_segment_id=sales_segment.id,
            order_url=self.request.route_url("cart.order", 
                    sales_segment_id=sales_segment.id),
            venue_name=sales_segment.performance.venue.name,
            event_id=self.request.context.event_id,
            venue_id=sales_segment.performance.venue.id,
            data_source=dict(
                venue_drawing=self.request.route_url(
                    'cart.venue_drawing',
                    event_id=self.request.context.event_id,
                    performance_id=sales_segment.performance.id,
                    venue_id=sales_segment.performance.venue.id,
                    part='__part__'),
                venue_drawings=self.get_frontend_drawing_urls(sales_segment.performance.venue),
                seats=self.request.route_url(
                    'cart.seats',
                    event_id=self.request.context.event_id,
                    sales_segment_id=sales_segment.id,
                    ),
                seat_adjacencies=self.request.application_url \
                    + api.get_route_pattern(
                      self.request.registry,
                      'cart.seat_adjacencies')
                )
            )
        return data

    @view_config(route_name='cart.products', renderer="json")
    @view_config(route_name='cart.products.obsolete', renderer="json")
    def get_products(self):
        """ 席種別ごとの購入単位
        SeatType -> ProductItem -> Product
        """
        seat_type_id = self.request.matchdict['seat_type_id']
        logger.debug("seat_typeid = %(seat_type_id)s, sales_segment_id = %(sales_segment_id)s"
            % dict(seat_type_id=seat_type_id, sales_segment_id=self.context.sales_segment.id))

        seat_type = DBSession.query(c_models.StockType).filter_by(id=seat_type_id).one()

        query = DBSession.query(c_models.Product, c_models.StockStatus.quantity) \
            .join(c_models.Product.items) \
            .join(c_models.ProductItem.stock) \
            .join(c_models.Stock.stock_status) \
            .filter(c_models.Stock.stock_type_id==seat_type_id) \
            .filter(c_models.Product.sales_segment_id==self.context.sales_segment.id) \
            .filter(c_models.Product.public==True) \
            .filter(c_models.ProductItem.deleted_at == None) \
            .filter(c_models.Stock.deleted_at == None) \
            .order_by(sa.desc("Product.display_order, Product.price"))

        products = [
            dict(
                id=p.id, 
                name=p.name,
                description=p.description,
                price=h.format_number(p.price, ","), 
                unit_template=h.build_unit_template(p, self.context.sales_segment.performance.id),
                quantity_power=p.get_quantity_power(seat_type, self.context.sales_segment.performance.id),
                upper_limit=p.sales_segment.upper_limit if p.sales_segment.upper_limit < vacant_quantity else int(vacant_quantity),
                )
            for p, vacant_quantity in query
            ]

        return dict(products=products,
                    seat_type=dict(id=seat_type.id, name=seat_type.name),
                    sales_segment=dict(
                        start_at=self.context.sales_segment.start_at.strftime("%Y-%m-%d %H:%M"),
                        end_at=self.context.sales_segment.end_at.strftime("%Y-%m-%d %H:%M")
                    ))

    @view_config(route_name='cart.seats', renderer="json")
    @view_config(route_name='cart.seats.obsolete', renderer="json")
    def get_seats(self):
        """会場&座席情報"""
        venue = self.context.performance.venue

        sales_segment = c_models.SalesSegment.query.filter(c_models.SalesSegment.id==self.context.sales_segment.id).one()
        sales_stocks = sales_segment.stocks

        return dict(
            seats=dict(
                (
                    seat.l0_id,
                    dict(
                        id=seat.l0_id,
                        stock_type_id=seat.stock.stock_type_id,
                        stock_holder_id=seat.stock.stock_holder_id,
                        status=seat.status,
                        areas=[area.id for area in seat.areas],
                        is_hold=seat.stock in sales_stocks,
                        )
                    ) 
                for seat in c_models.Seat.query_sales_seats(sales_segment)\
                             .options(joinedload('areas'),
                                      joinedload('status_'))\
                             .join(c_models.SeatStatus)\
                             .join(c_models.Stock)\
                             .filter(c_models.Seat.venue_id==venue.id)\
                             .filter(c_models.SeatStatus.status==int(c_models.SeatStatusEnum.Vacant))
                ),
            areas=dict(
                (area.id, { 'id': area.id, 'name': area.name }) \
                for area in DBSession.query(c_models.VenueArea) \
                            .join(c_models.VenueArea_group_l0_id) \
                            .filter(c_models.VenueArea_group_l0_id.venue_id==venue.id)
                ),
            info=dict(
                available_adjacencies=[
                    adjacency_set.seat_count
                    for adjacency_set in \
                        DBSession.query(c_models.SeatAdjacencySet) \
                        .filter_by(site_id=venue.site_id)
                    ]
                ),
            pages=get_venue_site_adapter(self.request, venue.site).get_frontend_pages()
            )

    @view_config(route_name='cart.seat_adjacencies', renderer="json")
    def get_seat_adjacencies(self):
        """連席情報"""
        try:
            venue_id = long(self.request.matchdict.get('venue_id'))
        except (ValueError, TypeError):
            venue_id = None
        try:
            performance_id = long(self.request.matchdict.get('performance_id'))
        except (ValueError, TypeError):
            performance_id = None

        if performance_id is None:
            raise HTTPNotFound()

        performance = DBSession.query(c_models.Performance).filter_by(id=performance_id).one()

        if performance.venue.id != venue_id:
            raise HTTPNotFound()
        length_or_range = self.request.matchdict['length_or_range']
        return dict(
            seat_adjacencies={
                length_or_range: [
                    [seat.l0_id for seat in seat_adjacency.seats_filter_by_venue(venue_id)]
                    for seat_adjacency_set in \
                        DBSession.query(c_models.SeatAdjacencySet)\
                            .filter_by(site_id=performance.venue.site_id, seat_count=length_or_range)
                    for seat_adjacency in seat_adjacency_set.adjacencies
                    ]
                }
            )

    @view_config(route_name="cart.venue_drawing", request_method="GET")
    def get_venue_drawing(self):
        try:
            venue_id = long(self.request.matchdict.get('venue_id'))
        except (ValueError, TypeError):
            venue_id = None
        try:
            performance_id = long(self.request.matchdict.get('performance_id'))
        except (ValueError, TypeError):
            performance_id = None

        if performance_id is None:
            raise HTTPNotFound()

        performance = DBSession.query(c_models.Performance).filter_by(id=performance_id).one()

        if performance.venue.id != venue_id:
            raise HTTPNotFound()
        part = self.request.matchdict.get('part')
        venue = c_models.Venue.get(venue_id)
        drawing = get_venue_site_adapter(self.request, venue.site).get_frontend_drawing(part)
        if not drawing:
            raise HTTPNotFound()
        content_encoding = None
        if re.match('^.+\.(svgz|gz)$', drawing.path):
            content_encoding = 'gzip'
        resp = Response(body=drawing.stream().read(), content_type='text/xml; charset=utf-8', content_encoding=content_encoding)
        if resp.content_encoding is None:
            resp.encode_content()
        return resp

@view_defaults(decorator=with_jquery)
class ReserveView(object):
    """ 座席選択完了画面(おまかせ) """

    product_id_regex = re.compile(r'product-(?P<product_id>\d+)')

    def __init__(self, request):
        self.request = request
        self.context = request.context


    def iter_ordered_items(self):
        for key, value in self.request.params.iteritems():
            m = self.product_id_regex.match(key)
            if m is None:
                continue
            quantity = int(value)
            logger.debug("key = %s, value = %s" % (key, value))
            if quantity == 0:
                continue
            yield m.groupdict()['product_id'], quantity

    @property
    def ordered_items(self):
        """ リクエストパラメータから(プロダクトID,数量)タプルのリストを作成する
        :return: list of tuple(ticketing.products.models.Product, int)
        """

        controls = list(self.iter_ordered_items())
        logger.debug('order %s' % controls)
        if len(controls) == 0:
            return []

        products = dict([(p.id, p) for p in DBSession.query(c_models.Product).filter(c_models.Product.id.in_([c[0] for c in controls]))])
        logger.debug('order %s' % products)

        return [(products.get(int(c[0])), c[1]) for c in controls]


    @view_config(route_name='cart.order', request_method="POST", renderer='json')
    def reserve(self):
        h.form_log(self.request, "received order")
        order_items = self.ordered_items
        if not order_items:
            return dict(result='NG', reason="no products")

        performance = c_models.Performance.query.filter(c_models.Performance.id==self.request.params['performance_id']).one()
        if not order_items:
            return dict(result='NG', reason="no performance")

        selected_seats = self.request.params.getall('selected_seat')
        logger.debug('order_items %s' % order_items)

        sum_quantity = 0
        if selected_seats:
            sum_quantity = len(selected_seats)
        else:
            for product, quantity in order_items:
                sum_quantity += quantity * product.get_quantity_power(product.seat_stock_type, product.performance_id)
        logger.debug('sum_quantity=%s' % sum_quantity)

        self.context.event_id = performance.event_id
        if self.context.sales_segment.upper_limit < sum_quantity:
            logger.debug('upper_limit over')
            return dict(result='NG', reason="upper_limit")

        try:
            cart = api.order_products(self.request, self.request.params['performance_id'], order_items, selected_seats=selected_seats)
            cart.sales_segment = self.context.sales_segment
            if cart is None:
                transaction.abort()
                return dict(result='NG')
        except NotEnoughAdjacencyException:
            transaction.abort()
            logger.debug("not enough adjacency")
            return dict(result='NG', reason="adjacency")
        except InvalidSeatSelectionException:
            transaction.abort()
            logger.debug("seat selection is invalid.")
            return dict(result='NG', reason="invalid seats")
        except InvalidProductSelectionException:
            transaction.abort()
            logger.debug("product selection is invalid.")
            return dict(result='NG', reason="invalid products")
        except NotEnoughStockException:
            transaction.abort()
            logger.debug("not enough stock quantity.")
            return dict(result='NG', reason="stock")
        except CartCreationException:
            transaction.abort()
            logger.debug("cannot create cart.")
            return dict(result='NG', reason="unknown")


        DBSession.add(cart)
        DBSession.flush()
        api.set_cart(self.request, cart)
        return dict(result='OK', 
                    payment_url=self.request.route_url("cart.payment", sales_segment_id=self.context.sales_segment.id),
                    cart=dict(products=[dict(name=p.product.name, 
                                             quantity=p.quantity,
                                             price=int(p.product.price),
                                             seats=p.seats,
                                             unit_template=h.build_unit_template(p.product, self.context.sales_segment.performance.id),
                                        )
                                        for p in cart.products],
                              total_amount=h.format_number(get_amount_without_pdmp(cart))
                             )
                    )



@view_defaults(decorator=with_jquery.not_when(mobile_request))
class ReleaseCartView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='cart.release', request_method="POST", renderer="json")
    def __call__(self):
        try:
            cart = api.get_cart_safe(self.request)
            cart.release()
            api.remove_cart(self.request)
        except NoCartError:
            import sys
            logger.info('exception ignored', exc_info=sys.exc_info())
        return dict()


@view_defaults(decorator=with_jquery.not_when(mobile_request))
class PaymentView(object):
    """ 支払い方法、引き取り方法選択 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @property
    def sales_segment(self):
        # contextから取れることを期待できないので
        # XXX: 会員区分からバリデーションしなくていいの?
        return c_models.SalesSegment.query.filter(c_models.SalesSegment.id==self.request.matchdict['sales_segment_id']).one()

    @view_config(route_name='cart.payment', request_method="GET", renderer=selectable_renderer("carts/%(membership)s/payment.html"))
    @view_config(route_name='cart.payment', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/payment.html"))
    def __call__(self):
        """ 支払い方法、引き取り方法選択
        """

        api.check_sales_segment_term(self.request)

        cart = api.get_cart_safe(self.request)
        self.context.event_id = cart.performance.event.id

        start_on = cart.performance.start_on
        sales_segment = self.sales_segment
        payment_delivery_methods = sales_segment.available_payment_delivery_method_pairs(getattr(self.context, 'now', datetime.now()))
        user = get_or_create_user(self.context.authenticated_user())
        user_profile = None
        if user is not None:
            user_profile = user.user_profile

        if user_profile is not None:
            formdata = MultiDict(
                last_name=user_profile.last_name,
                last_name_kana=user_profile.last_name_kana,
                first_name=user_profile.first_name,
                first_name_kana=user_profile.first_name_kana,
                tel_1=user_profile.tel_1,
                fax=getattr(user_profile, "fax", None), 
                zip=user_profile.zip,
                prefecture=user_profile.prefecture,
                city=user_profile.city,
                address_1=user_profile.address_1,
                address_2=user_profile.address_2,
                email_1=user_profile.email_1,
                email_2=user_profile.email_2
                )
        else:
            formdata = None

        form = schemas.ClientForm(formdata=formdata)
        return dict(form=form,
            payment_delivery_methods=payment_delivery_methods,
            #user=user, user_profile=user.user_profile,
            )

    def get_validated_address_data(self):
        """フォームから ShippingAddress などの値を取りたいときはこれで"""
        form = self.form
        if form.validate():
            return dict(
                first_name=form.data['first_name'],
                last_name=form.data['last_name'],
                first_name_kana=form.data['first_name_kana'],
                last_name_kana=form.data['last_name_kana'],
                zip=form.data['zip'],
                prefecture=form.data['prefecture'],
                city=form.data['city'],
                address_1=form.data['address_1'],
                address_2=form.data['address_2'],
                country=u"日本国",
                email_1=form.data['email_1'],
                email_2=form.data['email_2'],
                tel_1=form.data['tel_1'],
                tel_2=None,
                fax=form.data['fax']
                )
        else:
            return None

    def _validate_extras(self, cart, payment_delivery_pair, shipping_address_params):
        if not payment_delivery_pair or shipping_address_params is None:
            if not payment_delivery_pair:
                self.request.session.flash(u"お支払／引取方法をお選びください")
                logger.debug("invalid : %s" % 'payment_delivery_method_pair_id')
            else:
                logger.debug("invalid : %s" % self.form.errors)

            self.context.event_id = cart.performance.event.id

            return False
        return True

    @back(back_to_top, back_to_product_list_for_mobile)
    @view_config(route_name='cart.payment', request_method="POST", renderer=selectable_renderer("carts/%(membership)s/payment.html"))
    @view_config(route_name='cart.payment', request_type='altair.mobile.interfaces.IMobileRequest', request_method="POST", renderer=selectable_renderer("carts_mobile/%(membership)s/payment.html"))
    def post(self):
        """ 支払い方法、引き取り方法選択
        """
        api.check_sales_segment_term(self.request)
        cart = api.get_cart_safe(self.request)
        user = get_or_create_user(self.context.authenticated_user())

        payment_delivery_method_pair_id = self.request.params.get('payment_delivery_method_pair_id', 0)
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter_by(id=payment_delivery_method_pair_id).first()

        self.form = schemas.ClientForm(formdata=self.request.params)
        shipping_address_params = self.get_validated_address_data()
        if not self._validate_extras(cart, payment_delivery_pair, shipping_address_params):
            start_on = cart.performance.start_on
            sales_segment = self.sales_segment
            payment_delivery_methods = sales_segment.available_payment_delivery_method_pairs(getattr(self.context, 'now', datetime.now()))
            return dict(form=self.form, payment_delivery_methods=payment_delivery_methods)

        cart.payment_delivery_pair = payment_delivery_pair
        cart.shipping_address = self.create_shipping_address(user, shipping_address_params)
        DBSession.add(cart)

        order = api.new_order_session(
            self.request,
            client_name=self.get_client_name(),
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            email_1=cart.shipping_address.email_1,
        )

        self.request.session['payment_confirm_url'] = self.request.route_url('payment.confirm')

        payment = Payment(cart, self.request)
        result = payment.call_prepare()
        if callable(result):
            return result
        return HTTPFound(self.request.route_url("payment.confirm"))

    def get_client_name(self):
        return self.request.params['last_name'] + self.request.params['first_name']

    def create_shipping_address(self, user, data):
        logger.debug('shipping_address=%r', data)
        return c_models.ShippingAddress(
            first_name=data['first_name'],
            last_name=data['last_name'],
            first_name_kana=data['first_name_kana'],
            last_name_kana=data['last_name_kana'],
            zip=data['zip'],
            prefecture=data['prefecture'],
            city=data['city'],
            address_1=data['address_1'],
            address_2=data['address_2'],
            country=data['country'],
            email_1=data['email_1'],
            email_2=data['email_2'],
            tel_1=data['tel_1'],
            tel_2=data['tel_2'],
            fax=data['fax'],
            user=user
        )

@view_defaults(decorator=with_jquery.not_when(mobile_request))
class ConfirmView(object):
    """ 決済確認画面 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='payment.confirm', request_method="GET", renderer=selectable_renderer("carts/%(membership)s/confirm.html"))
    @view_config(route_name='payment.confirm', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/confirm.html"))
    def get(self):
        api.check_sales_segment_term(self.request)
        form = schemas.CSRFSecureForm(csrf_context=self.request.session)
        cart = api.get_cart_safe(self.request)

        magazines_to_subscribe = get_magazines_to_subscribe(cart.performance.event.organization, cart.shipping_address.emails)

        payment = Payment(cart, self.request)
        try:
            delegator = payment.call_delegator()
        except PaymentDeliveryMethodPairNotFound:
            raise HTTPFound(self.request.route_path("cart.payment", sales_segment_id=cart.sales_segment_id))
        return dict(
            cart=cart,
            mailmagazines_to_subscribe=magazines_to_subscribe,
            form=form,
            delegator=delegator,
        )


@view_defaults(decorator=with_jquery.not_when(mobile_request))
class CompleteView(object):
    """ 決済完了画面"""
    def __init__(self, request):
        self.request = request
        self.context = request.context
        # TODO: Orderを表示？

    @back(back_to_top, back_to_product_list_for_mobile)
    @view_config(route_name='payment.finish', renderer=selectable_renderer("carts/%(membership)s/completion.html"), request_method="POST")
    @view_config(route_name='payment.finish', request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("carts_mobile/%(membership)s/completion.html"), request_method="POST")
    def __call__(self):
        api.check_sales_segment_term(self.request)
        form = schemas.CSRFSecureForm(formdata=self.request.params, csrf_context=self.request.session)
        if not form.validate():
            logger.info('invalid csrf token: %s' % form.errors)
            raise InvalidCSRFTokenException

        # セッションからCSRFトークンを削除して再利用不可にしておく
        if 'csrf' in self.request.session:
            del self.request.session['csrf']
            self.request.session.persist()

        cart = api.get_cart_safe(self.request)
        if not cart.is_valid():
            raise NoCartError()

        payment = Payment(cart, self.request)
        order = payment.call_payment()

        notify_order_completed(self.request, order)

        # メール購読でエラーが出てロールバックされても困る
        transaction.commit()

        del self.request._cart
        cart = api.get_cart(self.request)
        order = DBSession.query(order.__class__).get(order.id)

        # メール購読
        user = get_or_create_user(self.context.authenticated_user())
        emails = cart.shipping_address.emails
        magazine_ids = self.request.params.getall('mailmagazine')
        multi_subscribe(user, emails, magazine_ids)

        api.remove_cart(self.request)
        api.logout(self.request)

        return dict(order=order)


@view_defaults(decorator=with_jquery.not_when(mobile_request))
class InvalidMemberGroupView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(context='.authorization.InvalidMemberGroupException')
    def __call__(self):
        event_id = self.context.event_id
        event = c_models.Event.query.filter(c_models.Event.id==event_id).one()
        location = api.get_valid_sales_url(self.request, event)
        logger.debug('url: %s ' % location)
        return HTTPFound(location=location)



@view_defaults(decorator=with_jquery.not_when(mobile_request))
class OutTermSalesView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(context='.exceptions.OutTermSalesException', renderer=selectable_renderer('ticketing.cart:templates/carts/%(membership)s/out_term_sales.html'))
    def pc(self):
        api.logout(self.request)
        if self.context.next is None:
            datum = self.context.last
            which = 'last'
        else:
            datum = self.context.next
            which = 'next'
        return dict(which=which, **datum)

    @view_config(context='.exceptions.OutTermSalesException', renderer=selectable_renderer('ticketing.cart:templates/carts_mobile/%(membership)s/out_term_sales.html'), 
        request_type='altair.mobile.interfaces.IMobileRequest')
    def mobile(self):
        api.logout(self.request)
        if self.context.next is None:
            datum = self.context.last
            which = 'last'
        else:
            datum = self.context.next
            which = 'next'
        return dict(which=which, **datum)

@view_config(decorator=with_jquery.not_when(mobile_request), route_name='cart.logout')
def logout(request):
    headers = security.forget(request)
    location = c_api.get_host_base_url(request)
    res = HTTPFound(location=location)
    res.headerlist.extend(headers)
    return res
