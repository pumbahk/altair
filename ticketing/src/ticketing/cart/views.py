# -*- coding:utf-8 -*-
import logging
import json
from datetime import datetime, timedelta
import re
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_
from markupsafe import Markup
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from js.jquery_tools import jquery_tools
from urllib2 import urlopen
from zope.deprecation import deprecate
from ..models import DBSession
from ..core import models as c_models
from ..orders import models as o_models
from ..users import models as u_models
from .models import Cart
from . import helpers as h
from . import schemas
from .exceptions import *
from .rakuten_auth.api import authenticated_user
from .events import notify_order_completed
from webob.multidict import MultiDict
from . import api
import transaction

logger = logging.getLogger(__name__)

class ExceptionView(object):
    def __init__(self, request):
        self.request = request

    @view_config(context=NoCartError)
    def handle_nocarterror(self):
        logger.error("No cart!")
        return HTTPFound('/')

class IndexView(object):
    """ 座席選択画面 """
    def __init__(self, request):
        self.request = request
        self.context = request.context


    @view_config(route_name='cart.index', renderer='carts_mobile/index.html', xhr=False, permission="view", request_type=".interfaces.IMobileRequest")
    @view_config(route_name='cart.index', renderer='carts/index.html', xhr=False, permission="view")
    def __call__(self):
        jquery_tools.need()
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.params.get('performance')

        from .api import get_event_info_from_cms
        event_extra_info = get_event_info_from_cms(self.request, event_id)
        logger.info(event_extra_info)

        e = DBSession.query(c_models.Event).filter_by(id=event_id).first()
        if e is None:
            raise HTTPNotFound(self.request.url)
        # 日程,会場,検索項目のコンボ用
        dates = sorted(list(set([p.start_on.strftime("%Y-%m-%d %H:%M") for p in e.performances])))
        # 日付ごとの会場リスト
        select_venues = {}
        for p in e.performances:
            d = p.start_on.strftime('%Y-%m-%d %H:%M')
            ps = select_venues.get(d, [])
            ps.append(dict(id=p.id, name=p.venue.name,
                           seat_types_url=self.request.route_url('cart.seat_types', performance_id=p.id,
                                                                 event_id=e.id)))
            select_venues[d] = ps

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

        sales_segment = self.context.get_sales_segument()
        if sales_segment is None:
            raise HTTPNotFound

        return dict(event=event,
                    dates=dates,
                    cart_release_url=self.request.route_url('cart.release'),
                    selected=Markup(json.dumps([selected_performance.id, selected_date])),
                    venues_selection=Markup(json.dumps(select_venues)),
                    products_from_selected_date_url = self.request.route_url("cart.date.products", event_id=event_id), 
                    order_url=self.request.route_url("cart.order"),
                    upper_limit=sales_segment.upper_limit,
                    event_extra_info=event_extra_info.get("event") or []
        )

    @view_config(route_name='cart.seat_types', renderer="json")
    def get_seat_types(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        seat_types = DBSession.query(c_models.StockType).filter(
            c_models.Performance.event_id==event_id).filter(
            c_models.Performance.id==performance_id).filter(
            c_models.Performance.event_id==c_models.StockHolder.event_id).filter(
            c_models.StockHolder.id==c_models.Stock.stock_holder_id).filter(
            c_models.Stock.stock_type_id==c_models.StockType.id).all()
        performance = c_models.Performance.query.filter_by(id=performance_id).one()
        data = dict(seat_types=[
                dict(id=s.id, name=s.name,
                    style=s.style,
                    products_url=self.request.route_url('cart.products',
                        event_id=event_id, performance_id=performance_id, seat_type_id=s.id),
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

        products = [dict(id=p.id, name=p.name, price=h.format_number(p.price, ","), unit_template=h.build_unit_template(p, performance_id))
            for p in query]

        return dict(products=products,
            seat_type=dict(id=seat_type.id, name=seat_type.name))

    @view_config(route_name='cart.seats', renderer="json")
    def get_seats(self):
        """会場&座席情報""" 
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        venue_id = self.request.matchdict['venue_id']
        return dict(
            seats=dict(
                (
                    seat.l0_id,
                    dict(
                        id=seat.l0_id,
                        stock_type_id=seat.stock_type_id,
                        status=seat.status,
                        areas=[area.id for area in seat.areas]
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
        
class Reserve2View(object):
    """ 座席選択完了画面(ユーザー選択) """
    def __init__(self, request):
        self.request = request

        # TODO: 座席選択コンポーネントへの入力を作る

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
                fax=user_profile.fax,
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
        cart.payment_delivery_pair = payment_delivery_pair

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
        shipping_address = o_models.ShippingAddress(
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
            fax=params['fax'],
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
