# -*- coding:utf-8 -*-
import logging
import transaction
import json
from datetime import datetime, timedelta
import re
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_
from markupsafe import Markup
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.exceptions import NotFound
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.threadlocal import get_current_request
from js.jquery_tools import jquery_tools
from urllib2 import urlopen
from zope.deprecation import deprecate
from ..models import DBSession
from ..core import models as c_models
from ..users import models as u_models
from .models import Cart
from . import helpers as h
from . import schemas
from .exceptions import CartException, NoCartError, NoEventError
from .rakuten_auth.api import authenticated_user
from .events import notify_order_completed
from webob.multidict import MultiDict
from . import api
from .reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from .stocker import NotEnoughStockException
import transaction

logger = logging.getLogger(__name__)

def back(func):
    def retval(*args, **kwargs):
        request = get_current_request()
        if request.params.has_key('back'):
            ReleaseCartView(request)()
            return HTTPFound(request.route_url('cart.index', event_id=request.params.get('event_id')))
        return func(*args, **kwargs)
    return retval

class IndexView(object):
    """ 座席選択画面 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='cart.index', renderer='carts/index.html', xhr=False, permission="buy")
    @view_config(route_name='cart.index.sales', renderer='carts/index.html', xhr=False, permission="buy")
    def __call__(self):
        jquery_tools.need()
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.params.get('performance')

        sales_segment = self.context.get_sales_segument()
        if sales_segment is None:
            logger.debug("No matching sales_segment")
            raise NoEventError("No matching sales_segment")

        from .api import get_event_info_from_cms
        event_extra_info = get_event_info_from_cms(self.request, event_id)
        logger.info(event_extra_info)

        e = DBSession.query(c_models.Event).filter_by(id=event_id).first()
        if e is None:
            raise NoEventError("No such event (%d)" % event_id)
        # 日程,会場,検索項目のコンボ用
        dates = sorted(list(set([p.start_on.strftime("%Y-%m-%d %H:%M") for p in e.performances])))
        logger.debug("dates:%s" % dates)
        # 日付ごとの会場リスト
        select_venues = {}
        for p in e.performances:
            d = p.start_on.strftime('%Y-%m-%d %H:%M')
            logger.debug('performance %d date %s' % (p.id, d))
            ps = select_venues.get(d, [])
            ps.append(dict(id=p.id, name=p.venue.name,
                           seat_types_url=self.request.route_url('cart.seat_types', 
                                                                 performance_id=p.id,
                                                                 sales_segment_id=sales_segment.id,
                                                                 event_id=e.id)))
            select_venues[d] = ps
        logger.debug("venues %s" % select_venues)

        # 会場
        venues = set([p.venue.name for p in e.performances])

        # TODO:支払い方法
        
        # TODO:引き取り方法

        if performance_id:
            # 指定公演とそれに紐づく会場
            selected_performance = c_models.Performance.query.filter(c_models.Performance.id==performance_id).first()
            selected_date = selected_performance.start_on.strftime('%Y-%m-%d %H:%M')

        else:
            # １つ目の会場の1つ目の公演
            selected_performance = e.performances[0]
            selected_date = selected_performance.start_on.strftime('%Y-%m-%d %H:%M')


        event = dict(id=e.id, code=e.code, title=e.title, abbreviated_title=e.abbreviated_title,
            sales_start_on=str(e.sales_start_on), sales_end_on=str(e.sales_end_on), venues=venues, product=e.products, )

        return dict(event=event,
                    dates=dates,
                    cart_release_url=self.request.route_url('cart.release'),
                    selected=Markup(json.dumps([selected_performance.id, selected_date])),
                    venues_selection=Markup(json.dumps(select_venues)),
                    sales_segment=Markup(json.dumps(dict(seat_choice=sales_segment.seat_choice))),
                    products_from_selected_date_url = self.request.route_url("cart.date.products", event_id=event_id), 
                    order_url=self.request.route_url("cart.order"),
                    upper_limit=sales_segment.upper_limit,
                    event_extra_info=event_extra_info.get("event") or []
        )

    @view_config(route_name='cart.seat_types', renderer="json")
    def get_seat_types(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        sales_segment_id = self.request.matchdict['sales_segment_id']

        segment_stocks = DBSession.query(c_models.ProductItem.stock_id).filter(
            c_models.ProductItem.product_id==c_models.Product.id).filter(
            c_models.Product.sales_segment_id==sales_segment_id)

        seat_types = DBSession.query(c_models.StockType).filter(
            c_models.Performance.event_id==event_id).filter(
            c_models.Performance.id==performance_id).filter(
            c_models.Performance.event_id==c_models.StockHolder.event_id).filter(
            c_models.StockHolder.id==c_models.Stock.stock_holder_id).filter(
            c_models.Stock.stock_type_id==c_models.StockType.id).filter(
            c_models.Stock.id.in_(segment_stocks)).filter(
            c_models.ProductItem.stock_id==c_models.Stock.id).filter(
            c_models.ProductItem.performance_id==performance_id).order_by(
            c_models.StockType.display_order).all()

        performance = c_models.Performance.query.filter_by(id=performance_id).one()

        data = dict(seat_types=[
                dict(id=s.id, name=s.name,
                    style=s.style,
                    products_url=self.request.route_url('cart.products',
                        event_id=event_id, performance_id=performance_id, seat_type_id=s.id),
                    quantity_only=s.quantity_only,
                    )
                for s in seat_types
                ],
                event_name=performance.event.title,
                performance_name=performance.name,
                performance_start=h.performance_date(performance),
                performance_id=performance_id,
                venue_name=performance.venue.name,
                event_id=event_id,
                venue_id=performance.venue.id,
                data_source=dict(
                    venue_drawing=self.request.route_url(
                        'cart.venue_drawing',
                        event_id=event_id,
                        performance_id=performance_id,
                        venue_id=performance.venue.id),
                    seats=self.request.route_url(
                        'cart.seats',
                        event_id=event_id,
                        performance_id=performance_id,
                        venue_id=performance.venue.id),
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
        query = query.filter(c_models.Product.id.in_(q)).order_by(sa.desc("price"))
        ### filter by salessegment
        salessegment = self.context.get_sales_segument()
        query = h.products_filter_by_salessegment(query, salessegment)


        products = [dict(name=p.name, price=h.format_number(p.price, ","), id=p.id)
                    for p in query]
        return dict(selected_date=selected_date_string, 
                    products=products)

    @view_config(route_name='cart.products', renderer="json")
    def get_products(self):
        """ 席種別ごとの購入単位 
        SeatType -> ProductItem -> Product
        """
        seat_type_id = self.request.matchdict['seat_type_id']
        performance_id = self.request.matchdict['performance_id']
       
        logger.debug("seat_typeid = %(seat_type_id)s, performance_id = %(performance_id)s"
            % dict(seat_type_id=seat_type_id, performance_id=performance_id))

        seat_type = DBSession.query(c_models.StockType).filter_by(id=seat_type_id).one()

        q = DBSession.query(c_models.ProductItem.product_id)
        q = q.filter(c_models.ProductItem.stock_id==c_models.Stock.id)
        q = q.filter(c_models.Stock.stock_type_id==seat_type_id)
        q = q.filter(c_models.ProductItem.performance_id==performance_id)

        query = DBSession.query(c_models.Product)
        query = query.filter(c_models.Product.id.in_(q)).order_by(sa.desc("price"))
        ### filter by salessegment
        salessegment = self.context.get_sales_segument()
        query = h.products_filter_by_salessegment(query, salessegment)

        products = [dict(id=p.id, 
                         name=p.name, 
                         price=h.format_number(p.price, ","), 
                         unit_template=h.build_unit_template(p, performance_id),
                         quantity_power=p.get_quantity_power(seat_type, performance_id))
            for p in query]

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
        venue_id = self.request.matchdict['venue_id']
        stock_holder = api.get_stock_holder(self.request, event_id)
        logger.debug("stock holder is %s:%s" % (stock_holder.id, stock_holder.name))
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
                        is_hold=seat.stock.stock_holder_id==stock_holder.id,
                        )
                    ) 
                for seat in DBSession.query(c_models.Seat) \
                            .options(joinedload('areas'),
                                     joinedload('status_')) \
                            .filter_by(venue_id=venue_id)
                ),
            areas=dict(
                (area.id, { 'id': area.id, 'name': area.name }) \
                for area in DBSession.query(c_models.VenueArea) \
                            .join(c_models.VenueArea_group_l0_id) \
                            .filter(c_models.VenueArea_group_l0_id.venue_id==venue_id)
                ),
            info=dict(
                available_adjacencies=[
                    adjacency_set.seat_count
                    for adjacency_set in \
                        DBSession.query(c_models.SeatAdjacencySet) \
                        .filter_by(venue_id=venue_id)
                    ]
                )
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
        venue_id = int(self.request.matchdict.get('venue_id', 0))
        venue = c_models.Venue.get(venue_id)
        return Response(app_iter=urlopen(venue.site.drawing_url), content_type='text/xml; charset=utf-8')

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
        order_items = self.ordered_items
        if not order_items:
            return dict(result='NG', reason="no products")

        performance = c_models.Performance.get(self.request.params['performance_id'])
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
        sales_segment = self.context.get_sales_segument()
        if sales_segment.upper_limit < sum_quantity:
            logger.debug('upper_limit over')
            return dict(result='NG', reason="upper_limit")

        try:
            cart = api.order_products(self.request, self.request.params['performance_id'], order_items, selected_seats=selected_seats)
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

        DBSession.add(cart)
        DBSession.flush()
        api.set_cart(self.request, cart)
        return dict(result='OK', 
                    payment_url=self.request.route_url("cart.payment"),
                    cart=dict(products=[dict(name=p.product.name, 
                                             quantity=p.quantity,
                                             price=int(p.product.price),
                                             seats=p.seats,
                                        ) 
                                        for p in cart.products],
                              total_amount=h.format_number(cart.tickets_amount),
                    ))

    @view_config(route_name='cart.order', request_method="POST", renderer='carts_mobile/reserve.html', request_type=".interfaces.IMobileRequest")
    def reserve_mobile(self):
        performance_id = self.request.params.get('performance_id')
        seat_type_id = self.request.params.get('seat_type_id')

        # パフォーマンス
        performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id).first()
        if performance is None:
            raise NoEventError("No such performance (%d)" % performance_id)
        # イベント
        event = performance.event

        # CSRFトークンの確認
        form = schemas.CSRFSecureForm(
            form_data=self.request.params,
            csrf_context=self.request.session)
        form.validate()

        data = dict(
            event=event,
            performance=performance, 
            seat_type_id=seat_type_id,
        )

        order_items = self.ordered_items
        try:
            # カート生成(席はおまかせ)
            cart = api.order_products(
                self.request,
                performance_id,
                order_items)
            if cart is None:
                transaction.abort()
                logger.debug("cart is None. aborted.")
                # TODO: 例外を上げる
                data.update(dict(result='NG'))
                return data
        except NotEnoughAdjacencyException:
            transaction.abort()
            logger.debug("not enough adjacency")
            data.update(dict(result='NG', reason="adjacency"))
            return data
        except InvalidSeatSelectionException:
            transaction.abort()
            logger.debug("seat selection is invalid.")
            data.update(dict(result='NG', reason="invalid seats"))
            return data
        except NotEnoughStockException as e:
            transaction.abort()
            logger.debug("not enough stock quantity :%s" % e)
            data.update(dict(result='NG', reason="stock"))
            return data

        DBSession.add(cart)
        DBSession.flush()
        api.set_cart(self.request, cart)
        data.update(dict(result='OK',
                    payment_url=self.request.route_url("cart.payment"),
                    cart=dict(products=[dict(name=p.product.name, 
                                             quantity=p.quantity,
                                             price=int(p.product.price),
                                             seats=p.seats,
                                        ) 
                                        for p in cart.products],
                              total_amount=h.format_number(cart.tickets_amount),
                    )))
        return data

    def __call__(self):
        """
        座席情報から座席グループを検索する
        """

        #seat_type_id = self.request.matchdict['seat_type_id']
        cart = self.context.order_products(self.request.params['performance_id'], self.ordered_items)
        if cart is None:
            return dict(result='NG')
        api.set_cart(self.request, cart)
        #self.request.session['ticketing.cart_id'] = cart.id
        #self.cart = cart
        return dict(result='OK', 
                    payment_url=self.request.route_url("cart.payment"),
                    cart=dict(products=[dict(name=p.product.name, 
                                             quantity=p.quantity,
                                             price=int(p.product.price),
                                        ) 
                                        for p in cart.products],
                              total_amount=h.format_number(cart.tickets_amount),
                    ))

    def on_error(self):
        """ 座席確保できなかった場合
        """

class ReleaseCartView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='cart.release', request_method="POST", renderer="json")
    def __call__(self):
        cart = api.get_cart(self.request)
        cart.release()
        DBSession.delete(cart)
        api.remove_cart(self.request)

        return dict()


class PaymentView(object):
    """ 支払い方法、引き取り方法選択 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='cart.payment', request_method="GET", renderer="carts/payment.html")
    @view_config(route_name='cart.payment', request_type='.interfaces.IMobileRequest', request_method="GET", renderer="carts_mobile/payment.html")
    def __call__(self):
        """ 支払い方法、引き取り方法選択
        """
        if not api.has_cart(self.request):
            raise NoCartError()
        cart = api.get_cart(self.request)
        self.context.event_id = cart.performance.event.id
        payment_delivery_methods = self.context.get_payment_delivery_method_pair()

        #openid = authenticated_user(self.request)
        #user = api.get_or_create_user(self.request, openid['clamed_id'])
        user = self.context.get_or_create_user()
        user_profile = user.user_profile
        if user_profile is not None:
            formdata = MultiDict(
                last_name=user_profile.last_name,
                last_name_kana=user_profile.last_name_kana,
                first_name=user_profile.first_name,
                first_name_kana=user_profile.first_name_kana,
                tel=user_profile.tel_1,
                fax=getattr(user_profile, "fax", None), 
                zip=user_profile.zip,
                prefecture=user_profile.prefecture,
                city=user_profile.city,
                address_1=user_profile.address_1,
                address_2=user_profile.address_2,
                mail_address=user_profile.email
                )
        else:
            formdata = None

        form = schemas.ClientForm(formdata=formdata)
        return dict(form=form,
            payment_delivery_methods=payment_delivery_methods,
            user=user, user_profile=user.user_profile)

    def validate(self):
        form = schemas.ClientForm(formdata=self.request.params)
        if form.validate():
            return None 
        else:
            return form

    @view_config(route_name='cart.payment', request_method="POST", renderer="carts/payment.html")
    @view_config(route_name='cart.payment', request_type='.interfaces.IMobileRequest', request_method="POST", renderer="carts_mobile/payment.html")
    def post(self):
        """ 支払い方法、引き取り方法選択
        """

        params = self.request.params
        if not api.has_cart(self.request):
            raise NoCartError()
        cart = api.get_cart(self.request)

        #openid = authenticated_user(self.request)
        #user = api.get_or_create_user(self.request, openid['clamed_id'])
        user = self.context.get_or_create_user()

        payment_delivery_method_pair_id = self.request.params.get('payment_delivery_method_pair_id', 0)
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter_by(id=payment_delivery_method_pair_id).first()
        if not payment_delivery_pair:
            self.request.session.flash(u"お支払い方法／受け取り方法をどれかひとつお選びください")
            raise HTTPFound(self.request.current_route_url())

        cart.payment_delivery_pair = payment_delivery_pair
        cart.system_fee = payment_delivery_pair.system_fee

        form = self.validate()

        #if not (payment_delivery_pair and form.validate()):
        if not payment_delivery_pair or form:
            self.context.event_id = cart.performance.event.id
            payment_delivery_methods = self.context.get_payment_delivery_method_pair()
            if not payment_delivery_pair:
                logger.debug("invalid : %s" % 'payment_delivery_method_pair_id')
            else:
                logger.debug("invalid : %s" % form.errors)
            return dict(form=form,
                payment_delivery_methods=payment_delivery_methods,
                user=user, user_profile=user.user_profile)

        shipping_address = self.create_shipping_address(user)

        DBSession.add(shipping_address)
        cart.shipping_address = shipping_address
        DBSession.add(cart)

        client_name = self.get_client_name()

        order = dict(
            client_name=client_name,
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            mail_address=shipping_address.email,
        )
        self.request.session['order'] = order

        payment_delivery_plugin = api.get_payment_delivery_plugin(self.request, 
            payment_delivery_pair.payment_method.payment_plugin_id,
            payment_delivery_pair.delivery_method.delivery_plugin_id,)
        if payment_delivery_plugin is not None:
            res = payment_delivery_plugin.prepare(self.request, cart)
            if res is not None and callable(res):
                return res
        else:
            payment_plugin = api.get_payment_plugin(self.request, payment_delivery_pair.payment_method.payment_plugin_id)
            res = payment_plugin.prepare(self.request, cart)
            if res is not None and callable(res):
                return res
        return HTTPFound(self.request.route_url("payment.confirm"))

    def get_client_name(self):
        return self.request.params['last_name'] + self.request.params['first_name']

    def create_shipping_address(self, user):
        params = self.request.params
        shipping_address = c_models.ShippingAddress(
            first_name=params['first_name'],
            last_name=params['last_name'],
            first_name_kana=params['first_name_kana'],
            last_name_kana=params['last_name_kana'],
            zip=params['zip'],
            prefecture=params['prefecture'],
            city=params['city'],
            address_1=params['address_1'],
            address_2=params['address_2'],
            #country=params['country'],
            country=u"日本国",
            tel_1=params['tel'],
            #tel_2=params['tel_2'],
            fax=params.get('fax'),
            user=user,
            email=params['mail_address']
        )
        return shipping_address


class ConfirmView(object):
    """ 決済確認画面 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='payment.confirm', request_method="GET", renderer="carts/confirm.html")
    @view_config(route_name='payment.confirm', request_type='.interfaces.IMobileRequest', request_method="GET", renderer="carts_mobile/confirm.html")
    def get(self):
        form = schemas.CSRFSecureForm(csrf_context=self.request.session)

        assert api.has_cart(self.request)
        cart = api.get_cart(self.request)

        magazines = u_models.MailMagazine.query.outerjoin(u_models.MailSubscription).filter(u_models.MailMagazine.organization==cart.performance.event.organization).filter(or_(u_models.MailSubscription.email != cart.shipping_address.email, u_models.MailSubscription.email == None)).all()

        user = self.context.get_or_create_user()
        return dict(cart=cart, mailmagazines=magazines, user=user, form=form)

    # @view_config(route_name='payment.confirm', request_method="POST", renderer="carts/confirm.html")
    # def post(self):

    #     assert h.has_cart(self.request)
    #     cart = h.get_cart(self.request)
    #         
    #     self.save_subscription()
    #     return HTTPFound(self.request.route_url("payment.finish"))


class CompleteView(object):
    """ 決済完了画面"""
    def __init__(self, request):
        self.request = request
        self.context = request.context
        # TODO: Orderを表示？

    @back
    @view_config(route_name='payment.finish', renderer="carts/completion.html", request_method="POST")
    @view_config(route_name='payment.finish', request_type='.interfaces.IMobileRequest', renderer="carts_mobile/completion.html", request_method="POST")
    def __call__(self):
        form = schemas.CSRFSecureForm(form_data=self.request.params, csrf_context=self.request.session)
        form.validate()
        #assert not form.csrf_token.errors
        assert api.has_cart(self.request)
        cart = api.get_cart(self.request)

        order_session = self.request.session['order']

        payment_delivery_method_pair_id = order_session['payment_delivery_method_pair_id']
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id
        ).one()

        payment_delivery_plugin = api.get_payment_delivery_plugin(self.request, 
            payment_delivery_pair.payment_method.payment_plugin_id,
            payment_delivery_pair.delivery_method.delivery_plugin_id,)
        if payment_delivery_plugin is not None:
            order = payment_delivery_plugin.finish(self.request, cart)
        else:
            payment_plugin = api.get_payment_plugin(self.request, payment_delivery_pair.payment_method.payment_plugin_id)
            order = payment_plugin.finish(self.request, cart)
            DBSession.add(order)
            delivery_plugin = api.get_delivery_plugin(self.request, payment_delivery_pair.delivery_method.delivery_plugin_id)
            delivery_plugin.finish(self.request, cart)

        #openid = authenticated_user(self.request)
        #user = api.get_or_create_user(self.request, openid['clamed_id'])
        user = self.context.get_or_create_user()
        order.user = user
        order.organization_id = order.performance.event.organization_id

        notify_order_completed(self.request, order)

        # メール購読でエラーが出てロールバックされても困る
        order_id = order.id
        mail_address = cart.shipping_address.email
        user_id = self.context.get_or_create_user().id
        transaction.commit()
        user = DBSession.query(user.__class__).get(user_id)
        order = DBSession.query(order.__class__).get(order_id)
 
        # メール購読
        self.save_subscription(user, mail_address)

        return dict(order=order)

    def save_subscription(self, user, mail_address):
        magazines = u_models.MailMagazine.query.all()

        # 購読
        magazine_ids = self.request.params.getall('mailmagazine')
        logger.debug("magazines: %s" % magazine_ids)
        for subscription in u_models.MailMagazine.query.filter(u_models.MailMagazine.id.in_(magazine_ids)).all():
            if subscription.subscribe(user, mail_address):
                logger.debug("User %s starts subscribing %s for <%s>" % (user, subscription.name, mail_address))
            else:
                logger.debug("User %s is already subscribing %s for <%s>" % (user, subscription.name, mail_address))


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


class MobileIndexView(object):
    """モバイルのパフォーマンス選択
    """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='cart.index', renderer='carts_mobile/index.html', xhr=False, permission="buy", request_type=".interfaces.IMobileRequest")
    @view_config(route_name='cart.index.sales', renderer='carts_mobile/index.html', xhr=False, permission="buy", request_type=".interfaces.IMobileRequest")
    def __call__(self):
        event_id = self.request.matchdict['event_id']
        venue_name = self.request.params.get('v')

        # セールスセグメント必須
        sales_segment = self.context.get_sales_segument()
        if sales_segment is None:
            raise NoEventError("No matching sales_segment")

        # パフォーマンスIDが確定しているなら商品選択へリダイレクト
        performance_id = self.request.params.get('pid')
        if performance_id:
            return HTTPFound(self.request.route_url(
                "cart.mobile",
                event_id=event_id,
                performance_id=performance_id))

        event = c_models.Event.query.filter(c_models.Event.id==event_id).first()
        if event is None:
            raise NoEventError("No such event (%d)" % event_id)

        if venue_name:
            venue = c_models.Venue.query.filter(c_models.Venue.name==venue_name).first()
            if venue is None:
                logger.debug("No such venue venue_name=%s" % venue_name)
        else:
            venue = None
        # 会場が指定されていなければ会場を選択肢を作る
        if venue:
            venues = []
            # 会場が確定しているならパフォーマンスの選択肢を作る
            performances_query = c_models.Performance.query \
                .filter(c_models.Performance.event_id==event_id)
            performances = [dict(id=p.id, start_on=p.start_on.strftime('%Y-%m-%d %H:%M')) \
                for p in performances_query if p.venue.name==venue_name]
        else:
            # 会場は会場名で一意にする
            venues = set(performance.venue.name for performance in event.performances)
            performances = []

        return dict(
            event=event,
            sales_segment=sales_segment,
            venue=venue,
            venues=venues,
            performances=performances,
        )


class MobileSelectProductView(object):
    """モバイルの商品選択
    """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='cart.mobile', renderer='carts_mobile/seat_types.html', xhr=False, permission="buy", request_type=".interfaces.IMobileRequest")
    def __call__(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        seat_type_id = self.request.params.get('stid')

        if seat_type_id:
            return HTTPFound(self.request.route_url(
                "cart.products",
                event_id=event_id,
                performance_id=performance_id,
                seat_type_id=seat_type_id))

        # セールスセグメント必須
        sales_segment = self.context.get_sales_segument()
        if sales_segment is None:
            raise NoEventError("No matching sales_segment")

        event = c_models.Event.query.filter(c_models.Event.id==event_id).first()
        if event is None:
            raise NoEventError("No such event (%d)" % event_id)

        performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id).filter(
            c_models.Performance.event_id==event.id).first()
        if performance is None:
            raise NoEventError("No such performance (%d)" % performance_id)

        segment_stocks = DBSession.query(c_models.ProductItem.stock_id).filter(
            c_models.ProductItem.product_id==c_models.Product.id).filter(
            c_models.Product.sales_segment_id==sales_segment.id)

        seat_types = DBSession.query(c_models.StockType).filter(
            c_models.Performance.event_id==event_id).filter(
            c_models.Performance.id==performance_id).filter(
            c_models.Performance.event_id==c_models.StockHolder.event_id).filter(
            c_models.StockHolder.id==c_models.Stock.stock_holder_id).filter(
            c_models.Stock.stock_type_id==c_models.StockType.id).filter(
            c_models.Stock.id.in_(segment_stocks)).filter(
            c_models.ProductItem.stock_id==c_models.Stock.id).filter(
            c_models.ProductItem.performance_id==performance_id).order_by(
            c_models.StockType.display_order).all()

        data = dict(
            seat_types=[
                dict(
                    id=s.id,
                    name=s.name
                )
            for s in seat_types
            ],
            event=event,
            performance=performance,
            venue=performance.venue,
        )
        return data

    @view_config(route_name='cart.products', renderer='carts_mobile/products.html', xhr=False, permission="buy", request_type=".interfaces.IMobileRequest")
    def products(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        seat_type_id = self.request.matchdict['seat_type_id']

        # セールスセグメント必須
        sales_segment = self.context.get_sales_segument()
        if sales_segment is None:
            raise NoEventError("No matching sales_segment")

        # イベント
        event = c_models.Event.query.filter(c_models.Event.id==event_id).first()
        if event is None:
            raise NoEventError("No such event (%d)" % event_id)

        # パフォーマンス(イベントにひもづいてること)
        performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id).filter(
            c_models.Performance.event_id==event.id).first()
        if performance is None:
            raise NoEventError("No such performance (%d)" % performance_id)

        # 席種(イベントとパフォーマンスにひもづいてること)
        segment_stocks = DBSession.query(c_models.ProductItem.stock_id).filter(
            c_models.ProductItem.product_id==c_models.Product.id).filter(
            c_models.Product.sales_segment_id==sales_segment.id)

        seat_type = DBSession.query(c_models.StockType).filter(
            c_models.Performance.event_id==event_id).filter(
            c_models.Performance.id==performance_id).filter(
            c_models.Performance.event_id==c_models.StockHolder.event_id).filter(
            c_models.StockHolder.id==c_models.Stock.stock_holder_id).filter(
            c_models.Stock.stock_type_id==c_models.StockType.id).filter(
            c_models.Stock.id.in_(segment_stocks)).filter(
            c_models.StockType.id==seat_type_id).first()

        if seat_type is None:
            raise NoEventError("No such seat_type (%s)" % seat_type_id)

        # 商品一覧
        # サブクエリの部分
        product_items = DBSession.query(c_models.ProductItem.product_id).filter(
            c_models.ProductItem.stock_id==c_models.Stock.id).filter(
            c_models.Stock.stock_type_id==seat_type_id).filter(
            c_models.ProductItem.performance_id==performance_id)

        products = c_models.Product.query.filter(
            c_models.Product.id.in_(product_items)).order_by(
            sa.desc("price")).filter_by(
            sales_segment=sales_segment)

        # CSRFトークン発行
        form = schemas.CSRFSecureForm(csrf_context=self.request.session)

        data = dict(
            event=event,
            performance=performance,
            venue=performance.venue,
            seat_type=seat_type,
            upper_limit=sales_segment.upper_limit,
            products=[
                dict(
                    id=product.id,
                    name=product.name,
                    detail=h.product_name_with_unit(product, performance_id),
                    price=h.format_number(product.price, ","),
                )
                for product in products
            ],
            form=form,
        )
        return data

class OutTermSalesView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(context='.exceptions.OutTermSalesException', renderer='ticketing.cart:templates/carts/out_term_sales.html')
    def __call__(self):
        return dict(event=self.context.event, sales_segment=self.context.sales_segment)
