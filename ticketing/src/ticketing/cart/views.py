# -*- coding:utf-8 -*-
import logging
import re
import json
import transaction
from collections import OrderedDict
from datetime import datetime, timedelta
from urllib2 import urlopen

import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from sqlalchemy import sql
from sqlalchemy.sql.expression import or_, select

from markupsafe import Markup

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.exceptions import NotFound
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid.threadlocal import get_current_request
from pyramid import security
from zope.deprecation import deprecate
from webob.multidict import MultiDict

import js.jquery, js.jquery_tools


from ticketing.models import DBSession
from ticketing.core import models as c_models
from ticketing.users import models as u_models
from ticketing.mailmags import models as mailmag_models
from ticketing.views import mobile_request
from ticketing.fanstatic import with_jquery, with_jquery_tools
from ticketing.rakuten_auth.api import authenticated_user
from ticketing.payments.payment import Payment
from ticketing.payments.exceptions import PaymentDeliveryMethodPairNotFound
from ticketing.mobile.interfaces import IMobileRequest

from . import api
from . import helpers as h
from . import schemas
from .models import Cart
from .events import notify_order_completed
from .reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from .stocker import NotEnoughStockException
from .selectable_renderer import selectable_renderer
from .api import get_seat_type_triplets
from .view_support import IndexViewMixin
from .exceptions import (
    CartException, 
    NoCartError, 
    NoEventError,
    NoPerformanceError,
    NoSalesSegment,
    InvalidCSRFTokenException, 
    OverQuantityLimitError, 
    ZeroQuantityError, 
    CartCreationExceptoion,
    OutTermSalesException,
    DeliveryFailedException,
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

    @view_config(decorator=with_jquery_tools, route_name='cart.index', renderer=selectable_renderer("carts/%(membership)s/index.html"), xhr=False, permission="buy")
    def __call__(self):
        self.check_redirect(mobile=False)
        sales_segments = self.context.available_sales_segments
        performances = [ss.performance for ss in sales_segments]

        select_venues = OrderedDict()

        for p in performances:
            select_venues[p.name] = []

        for sales_segment in sales_segments:
            performance = sales_segment.performance
            pname = performance.name
            select_venues[pname].append(dict(
                id=performance.id,
                name=u'{start:%Y-%m-%d %H:%M}開始 {vname} {name}'.format(name=sales_segment.name, start=performance.start_on, vname=performance.venue.name),
                order_url=self.request.route_url("cart.order", sales_segment_id=sales_segment.id),
                upper_limit=sales_segment.upper_limit,
                seat_types_url=self.request.route_url('cart.seat_types',
                    performance_id=performance.id,
                    sales_segment_id=sales_segment.id,
                    event_id=self.context.event.id)))
            
        logger.debug("venues %s" % select_venues)

        # 会場
        venues = set([p.venue.name for p in self.context.event.performances])

        performance_id = self.request.params.get('pid') or self.request.params.get('performance')

        if not performance_id:
            # GETパラメータ指定がなければ、選択肢の1つ目を採用
            #performance_id = performances[0][1][0]['pid']
            performance_id = performances[0].id

        selected_performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id
        ).filter(
            c_models.Performance.event_id==self.context.event_id
        ).filter(
            c_models.Performance.public == True
        ).first()

        if selected_performance is None and performance_id is not None:
            raise NoPerformanceError(event_id=self.context.event.id)

        return dict(
            event=dict(
                id=self.context.event.id,
                code=self.context.event.code,
                title=self.context.event.title,
                abbreviated_title=self.context.event.abbreviated_title,
                sales_start_on=str(self.context.event.sales_start_on),
                sales_end_on=str(self.context.event.sales_end_on),
                venues=venues,
                product=self.context.event.products
                ),
            dates=sorted(list(set([p.start_on.strftime("%Y-%m-%d %H:%M") for p in self.context.event.performances]))),
            cart_release_url=self.request.route_url('cart.release'),
            selected=Markup(
                json.dumps([
                    selected_performance.name,
                    selected_performance.id])),
            venues_selection=Markup(json.dumps(select_venues.items())),
            products_from_selected_date_url=self.request.route_url(
                "cart.date.products",
                event_id=self.context.event_id), 
            event_extra_info=self.event_extra_info.get("event") or []
            )

    @view_config(route_name='cart.seat_types', renderer="json")
    def get_seat_types(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        sales_segment_id = self.request.matchdict['sales_segment_id']
        #performance = c_models.Performance.query.filter_by(id=performance_id).one()
        performance = self.request.context.performance

        seat_type_triplets = get_seat_type_triplets(event_id, performance_id, sales_segment_id)
        data = dict(
            seat_types=[
                dict(
                    id=s.id,
                    name=s.name,
                    description=s.description,
                    style=s.style,
                    products_url=self.request.route_url('cart.products',
                        event_id=event_id, performance_id=performance_id, sales_segment_id=sales_segment_id, seat_type_id=s.id),
                    availability=available > 0,
                    availability_text=h.get_availability_text(available),
                    quantity_only=s.quantity_only,
                    )
                for s, total, available in seat_type_triplets
                ],
            event_name=performance.event.title,
            performance_name=performance.name,
            performance_start=h.performance_date(performance),
            performance_id=performance_id,
            sales_segment_id=sales_segment_id,
            order_url=self.request.route_url("cart.order", 
                    sales_segment_id=sales_segment_id),
            venue_name=performance.venue.name,
            event_id=event_id,
            venue_id=performance.venue.id,
            data_source=dict(
                venue_drawing=self.request.route_url(
                    'cart.venue_drawing',
                    event_id=event_id,
                    performance_id=performance_id,
                    venue_id=performance.venue.id,
                    part='__part__'),
                seats=self.request.route_url(
                    'cart.seats',
                    event_id=event_id,
                    performance_id=performance_id,
                    #venue_id=performance.venue.id,
                    sales_segment_id=sales_segment_id,
                    ),
                seat_adjacencies=self.request.application_url \
                    + api.get_route_pattern(
                      self.request.registry,
                      'cart.seat_adjacencies')
                )
            )
        return data

    @view_config(route_name="cart.date.products", renderer="json")
    def get_products_with_date(self):
        """ 公演日ごとの購入単位
        (event_id, venue, date) -> [performance] -> [productitems] -> [product]

        need: request.GET["selected_date"] # e.g. format: 2011-11-11
        """

        if 'selected_date' not in self.request.GET:
            return dict()

        selected_date_string = self.request.GET["selected_date"]
        event_id = self.request.matchdict["event_id"]

        logger.debug("event_id = %(event_id)s, selected_date = %(selected_date)s"
            % dict(event_id=event_id, selected_date=selected_date_string))

        selected_date = datetime.strptime(selected_date_string, "%Y-%m-%d %H:%M")

        ## selected_dateが==で良いのはself.__call__で指定された候補を元に選択されるから
        q = DBSession.query(c_models.ProductItem.product_id)
        q = q.filter(c_models.Performance.event_id==event_id)
        q = q.filter(c_models.Performance.start_on==selected_date)
        q = q.filter(c_models.Performance.id == c_models.ProductItem.performance_id)

        query = DBSession.query(c_models.Product)
        query = query.filter(c_models.Product.public==True)
        query = query.filter(c_models.Product.id.in_(q)).order_by(sa.desc("display_order, price"))
        ### filter by salessegment
        query = h.products_filter_by_salessegment(query, self.context.sales_segment)

        products = [
            dict(
                id=p.id,
                name=p.name,
                description=p.description,
                price=h.format_number(p.price, ",")
                )
            for p in query
            ]
        return dict(selected_date=selected_date_string, 
                    products=products)

    @view_config(route_name='cart.products', renderer="json")
    def get_products(self):
        """ 席種別ごとの購入単位
        SeatType -> ProductItem -> Product
        """
        seat_type_id = self.request.matchdict['seat_type_id']
        performance_id = self.request.matchdict['performance_id']
        sales_segment_group_id = self.request.matchdict['sales_segment_id']
       
        logger.debug("seat_typeid = %(seat_type_id)s, performance_id = %(performance_id)s"
            % dict(seat_type_id=seat_type_id, performance_id=performance_id))

        seat_type = DBSession.query(c_models.StockType).filter_by(id=seat_type_id).one()

        q = DBSession.query(c_models.ProductItem.product_id)
        q = q.filter(c_models.ProductItem.stock_id==c_models.Stock.id)
        q = q.filter(c_models.Stock.stock_type_id==seat_type_id)
        q = q.filter(c_models.ProductItem.performance_id==performance_id)

        query = DBSession.query(c_models.Product)
        query = query.filter(c_models.Product.public==True)
        query = query.filter(c_models.Product.id.in_(q)).order_by(sa.desc("display_order, price"))
        ### filter by salessegment
        salessegment = DBSession.query(c_models.SalesSegment).filter_by(id=sales_segment_group_id).one()
        query = h.products_filter_by_salessegment(query, salessegment)

        products = [
            dict(
                id=p.id, 
                name=p.name, 
                description=p.description,
                price=h.format_number(p.price, ","), 
                unit_template=h.build_unit_template(p, performance_id),
                quantity_power=p.get_quantity_power(seat_type, performance_id),
                upper_limit=p.sales_segment.upper_limit,
                )
            for p in query
            ]

        return dict(products=products,
                    seat_type=dict(id=seat_type.id, name=seat_type.name),
                    sales_segment=dict(
                        start_at=salessegment.start_at.strftime("%Y-%m-%d %H:%M"),
                        end_at=salessegment.end_at.strftime("%Y-%m-%d %H:%M")
                    ))

    @view_config(route_name='cart.seats', renderer="json")
    def get_seats(self):
        """会場&座席情報""" 
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        sales_segment_id = self.request.matchdict['sales_segment_id']
        performance = c_models.Performance.query.filter(c_models.Performance.id==performance_id).one()
        venue = performance.venue

        sales_segment = c_models.SalesSegment.query.filter(c_models.SalesSegment.id==sales_segment_id).one()
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
                        .filter_by(venue_id=venue.id)
                    ]
                ),
            pages=venue.site._metadata and venue.site._metadata.get('pages')
            )

    @view_config(route_name='cart.seat_adjacencies', renderer="json")
    def get_seat_adjacencies(self):
        """連席情報""" 
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        venue_id = self.request.matchdict['venue_id']
        length_or_range = self.request.matchdict['length_or_range']
        return dict(
            seat_adjacencies={
                length_or_range: [
                    [seat.l0_id for seat in seat_adjacency.seats]
                    for seat_adjacency_set in \
                        DBSession.query(c_models.SeatAdjacencySet) \
                        .options(joinedload("adjacencies"),
                                 joinedload('adjacencies.seats')) \
                        .filter_by(venue_id=venue_id,
                                   seat_count=length_or_range)
                    for seat_adjacency in seat_adjacency_set.adjacencies 
                    ]
                }
            )

    @view_config(route_name="cart.venue_drawing", request_method="GET")
    def get_venue_drawing(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        venue_id = self.request.matchdict.get('venue_id')
        if not venue_id:
            raise HTTPNotFound()
        part = self.request.matchdict.get('part')
        venue = c_models.Venue.get(venue_id)
        drawing = venue.site.get_drawing(part)
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

        performance = c_models.Performance.query.filter(c_models.Performance.id==self.request.params['performance_id']).with_lockmode('update').one()
        if not order_items:
            return dict(result='NG', reason="no performance")

        selected_seats = self.request.params.getall('selected_seat')
        logger.debug('order_items %s' % order_items)

        sum_quantity = 0
        if selected_seats:
            sum_quantity = len(selected_seats)
        else:
            for product, quantity in order_items:
                sum_quantity += quantity
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
        except NotEnoughStockException as e:
            transaction.abort()
            logger.debug("not enough stock quantity :%s" % e)
            return dict(result='NG', reason="stock")
        except CartCreationExceptoion as e:
            transaction.abort()
            logger.debug("cannot create cart :%s" % e)
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
                                        ) 
                                        for p in cart.products],
                              total_amount=h.format_number(cart.tickets_amount),
                    ))



@view_defaults(decorator=with_jquery.not_when(mobile_request))
class ReleaseCartView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='cart.release', request_method="POST", renderer="json")
    def __call__(self):
        cart = api.get_cart(self.request)
        cart.release()
        api.remove_cart(self.request)

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
    @view_config(route_name='cart.payment', request_type='ticketing.mobile.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/payment.html"))
    def __call__(self):
        """ 支払い方法、引き取り方法選択
        """

        api.check_sales_segment_term(self.request)

        cart = api.get_cart_safe(self.request)
        self.context.event_id = cart.performance.event.id

        start_on = cart.performance.start_on
        #payment_delivery_methods = self.context.get_payment_delivery_method_pair(start_on=start_on)
        sales_segment = self.sales_segment
        payment_delivery_methods = sales_segment.available_payment_delivery_method_pairs
        user = self.context.get_or_create_user()
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
                self.request.session.flash(u"お支払い方法／受け取り方法をどれかひとつお選びください")
                logger.debug("invalid : %s" % 'payment_delivery_method_pair_id')
            else:
                logger.debug("invalid : %s" % self.form.errors)

            self.context.event_id = cart.performance.event.id

            return False
        return True

    @back(back_to_top, back_to_product_list_for_mobile)
    @view_config(route_name='cart.payment', request_method="POST", renderer=selectable_renderer("carts/%(membership)s/payment.html"))
    @view_config(route_name='cart.payment', request_type='ticketing.mobile.interfaces.IMobileRequest', request_method="POST", renderer=selectable_renderer("carts_mobile/%(membership)s/payment.html"))
    def post(self):
        """ 支払い方法、引き取り方法選択
        """
        api.check_sales_segment_term(self.request)
        cart = api.get_cart_safe(self.request)
        user = self.context.get_or_create_user()

        payment_delivery_method_pair_id = self.request.params.get('payment_delivery_method_pair_id', 0)
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter_by(id=payment_delivery_method_pair_id).first()

        self.form = schemas.ClientForm(formdata=self.request.params)
        shipping_address_params = self.get_validated_address_data()
        if not self._validate_extras(cart, payment_delivery_pair, shipping_address_params):
            start_on = cart.performance.start_on
            sales_segment = self.sales_segment
            payment_delivery_methods = sales_segment.available_payment_delivery_method_pairs
            return dict(form=self.form, payment_delivery_methods=payment_delivery_methods)

        cart.payment_delivery_pair = payment_delivery_pair
        cart.system_fee = payment_delivery_pair.system_fee
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
    @view_config(route_name='payment.confirm', request_type='ticketing.mobile.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/confirm.html"))
    def get(self):
        api.check_sales_segment_term(self.request)
        form = schemas.CSRFSecureForm(csrf_context=self.request.session)
        cart = api.get_cart_safe(self.request)

        # == MailMagazineに移動 ==
        magazines_to_subscribe = cart.performance.event.organization.mail_magazines \
            .filter(
                ~mailmag_models.MailMagazine.id.in_(
                    DBSession.query(mailmag_models.MailMagazine.id) \
                        .join(mailmag_models.MailSubscription.segment) \
                        .filter(
                            mailmag_models.MailSubscription.email.in_(cart.shipping_address.emails) & \
                            (mailmag_models.MailSubscription.status.in_([
                                mailmag_models.MailSubscriptionStatus.Subscribed.v,
                                mailmag_models.MailSubscriptionStatus.Reserved.v]) | \
                             (mailmag_models.MailSubscription.status == None)) \
                            ) \
                        .distinct()
                    )
                ) \
            .all()

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
    @view_config(route_name='payment.finish', request_type='ticketing.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("carts_mobile/%(membership)s/completion.html"), request_method="POST")
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
        user = self.context.get_or_create_user()
        emails = cart.shipping_address.emails
        magazine_ids = self.request.params.getall('mailmagazine')
        mailmag_models.MailMagazine.multi_subscribe(user, emails, magazine_ids)

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
        request_type='ticketing.mobile.interfaces.IMobileRequest')
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
    res = HTTPFound(location='/')
    res.headerlist.extend(headers)
    return res
