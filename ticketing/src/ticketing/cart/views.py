# -*- coding:utf-8 -*-
import logging
import json
import re
from markupsafe import Markup
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.decorator import reify
from ticketing.models import DBSession
import ticketing.events.models as e_models
import ticketing.products.models as p_models
from . import helpers as h

logger = logging.getLogger(__name__)

class IndexView(object):
    """ 座席選択画面 """
    def __init__(self, request):
        self.request = request

    
    @view_config(route_name='cart.index', renderer='ticketing:templates/carts/index.html', xhr=False)
    def __call__(self):
        event_id = self.request.matchdict['event_id']
        e = DBSession.query(e_models.Event).filter_by(id=event_id).first()
        if e is None:
            raise HTTPNotFound(self.request.url)
        # 日程,会場,検索項目のコンボ用
        dates = sorted(list(set([p.start_on.strftime("%Y-%m-%d") for p in e.performances])))
        # 日付ごとの会場リスト
        select_venues = {}
        for p in e.performances:
            d = p.start_on.strftime('%Y-%m-%d')
            ps = select_venues.get(d, [])
            ps.append(dict(id=p.id, name=p.venue.name,
                           seat_types_url=self.request.route_url('cart.seat_types', performance_id=p.id,
                                                                 event_id=e.id)))
            select_venues[d] = ps

        # 会場
        venues = set([p.venue.name for p in e.performances])

        # TODO:支払い方法
        
        # TODO:引き取り方法
        
        return dict(event=dict(id=e.id, code=e.code, title=e.title, abbreviated_title=e.abbreviated_title,
                               start_on=str(e.start_on), end_on=str(e.end_on),
                               sales_start_on=str(e.sales_start_on), 
                               sales_end_on=str(e.sales_end_on),
                               venues=venues,
                               product=e.product),
                    dates=dates,
                    venues_selection=Markup(json.dumps(select_venues)))

    @view_config(route_name='cart.seat_types', renderer="json")
    def get_seat_types(self):
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.matchdict['performance_id']
        seat_types = DBSession.query(p_models.SeatType).filter(
            e_models.Performance.event_id==event_id).filter(
            e_models.Performance.id==performance_id).filter(
                p_models.SeatType.performance_id==e_models.Performance.id).all()
            
        data = dict(seat_types=[
                dict(id=s.id, name=s.name,
                    products_url=self.request.route_url('cart.products',
                        event_id=event_id, performance_id=performance_id, seat_type_id=s.id),
                    )
                for s in seat_types
                ])
        print data
        return data

    @view_config(route_name='cart.products', renderer="json")
    def get_products(self):
        """ 席種別ごとの購入単位 
        SeatType -> ProductItem -> Product
        """
        seat_type_id = self.request.matchdict['seat_type_id']
        performance_id = self.request.matchdict['performance_id']

        seat_type = DBSession.query(p_models.SeatType).filter_by(id=seat_type_id).one()

        q = DBSession.query(p_models.ProductItem.product_id).filter(
            p_models.ProductItem.seat_type_id==seat_type_id).filter(
            p_models.ProductItem.performance_id==performance_id)
            
        query = DBSession.query(p_models.Product).filter(
            p_models.Product.id.in_(q))

        products = [dict(id=p.id, name=p.name, price=h.format_number(p.price, ","))
            for p in query]
        print products
        return dict(products=products,
            seat_type=dict(id=seat_type.id, name=seat_type.name))


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
            yield m.groupdict()['product_id'], int(value)

    @reify
    def ordered_items(self):
        """ リクエストパラメータから(プロダクトID,数量)タプルのリストを作成する
        :return: list of tuple(ticketing.products.models.Product, int)
        """

        controls = list(self.iter_ordered_items())
        if len(controls) == 0:
            return []

        products = dict([(p.id, p) for p in DBSession.query(p_models.Product).filter(p_models.Product.id.in_([c[0] for c in controls]))])

        return [(products.get(int(c[0])), c[1]) for c in controls]


    @view_config(route_name='cart.order', renderer='json')
    def __call__(self):
        """
        座席情報から座席グループを検索する
        """

        #seat_type_id = self.request.matchdict['seat_type_id']
        cart = self.context.order_products(self.ordered_items)
        if cart is None:
            return dict(result='NG')
        self.request.session['ticketing.cart_id'] = cart.id
        self.cart = cart
        return dict(result='OK')

    def on_error(self):
        """ 座席確保できなかった場合
        """

class Reserve2View(object):
    """ 座席選択完了画面(ユーザー選択) """
    def __init__(self, request):
        self.request = request

        # TODO: 座席選択コンポーネントへの入力を作る

class PaymentView(object):
    """ 支払い方法、引き取り方法選択 """
    def __init__(self, request):
        self.request = request

        # TODO: PaymentMethodPairあたりを取得


class ConfirmView(object):
    """ 決済確認画面 """
    def __init__(self, request):
        self.request = request
        # TODO: Cart内容を表示？

class CompleteView(object):
    """ 決済完了画面"""
    def __init__(self, request):
        self.request = request
        # TODO: Orderを表示？