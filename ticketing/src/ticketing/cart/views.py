# -*- coding:utf-8 -*-
import logging
import json
import re
from markupsafe import Markup
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config
from js.jquery_tools import jquery_tools
from ..models import DBSession
from ..core import models as c_models
from ..orders import models as o_models
from . import helpers as h
from ..multicheckout import helpers as m_h
from ..multicheckout import api as multicheckout_api
from . import schema
from .rakuten_auth.api import authenticated_user
from . import plugins

logger = logging.getLogger(__name__)

class IndexView(object):
    """ 座席選択画面 """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    
    @view_config(route_name='cart.index', renderer='carts/index.html', xhr=False, permission="view")
    def __call__(self):
        jquery_tools.need()
        event_id = self.request.matchdict['event_id']
        performance_id = self.request.params.get('performance')
        e = DBSession.query(c_models.Event).filter_by(id=event_id).first()
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

        if performance_id:
            # 指定公演とそれに紐づく会場
            selected_performance = c_models.Performance.query.filter(c_models.Performance.id==performance_id).first()
            selected_date = selected_performance.start_on.strftime('%Y-%m-%d')
            pass
        else:
            # １つ目の会場の1つ目の公演
            selected_performance = e.performances[0]
            selected_date = selected_performance.start_on.strftime('%Y-%m-%d')
            pass

        event = dict(id=e.id, code=e.code, title=e.title, abbreviated_title=e.abbreviated_title,
            first_start_on=str(e.first_start_on), final_start_on=str(e.final_start_on),
            sales_start_on=str(e.sales_start_on), sales_end_on=str(e.sales_end_on), venues=venues, product=e.products, )

        sales_segment = self.context.get_sales_segument()

        return dict(event=event,
                    dates=dates,
                    selected=Markup(json.dumps([selected_performance.id, selected_date])),
                    venues_selection=Markup(json.dumps(select_venues)),
                    order_url=self.request.route_url("cart.order"),
                    upper_limit=sales_segment.upper_limit,
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
            
        data = dict(seat_types=[
                dict(id=s.id, name=s.name,
                    products_url=self.request.route_url('cart.products',
                        event_id=event_id, performance_id=performance_id, seat_type_id=s.id),
                    )
                for s in seat_types
                ],
                performance_id=performance_id,
                )
        return data

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
        query = query.filter(c_models.Product.id.in_(q))

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
        h.set_cart(self.request, cart)
        #self.request.session['ticketing.cart_id'] = cart.id
        #self.cart = cart
        return dict(result='OK', 
                    pyament_url=self.request.route_url("cart.payment"),
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
    def __call__(self):
        """ 支払い方法、引き取り方法選択
        """
        if not h.has_cart(self.request):
            return HTTPFound('/')
        cart = h.get_cart(self.request)
        self.context.event_id = cart.performance.event.id
        payment_delivery_methods = self.context.get_payment_delivery_method_pair()

        return dict(payment_delivery_methods=payment_delivery_methods)

    @view_config(route_name='cart.payment', request_method="POST", renderer="carts/payment.html")
    def post(self):
        """ 支払い方法、引き取り方法選択
        """

        payment_delivery_pair_id = self.request.params['payment_delivery_pair_id']

        order = dict(
            client_name=self.request.params['client_name'],
            mail_address=self.request.params['mail_address'],
            payment_delivery_pair_id=payment_delivery_pair_id,
        )
        self.request.session['order'] = order

        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.id==payment_delivery_pair_id
        ).one()

        # TODO: マジックナンバー
        if payment_delivery_pair.payment_method_id == 3:
            raise HTTPFound(self.request.route_url("payment.secure3d"))
        raise HTTPFound(self.request.route_url("payment.confirm"))

class MultiCheckoutView(object):
    """ マルチ決済API
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='payment.secure3d', request_method="GET", renderer='carts/card_form.html')
    def card_info_secure3d_form(self):
        """ カード情報入力"""
        return dict()

    @view_config(route_name='payment.secure3d', request_method="POST", renderer='carts/redirect_post.html')
    def card_info_secure3d(self):
        """ カード情報入力(3Dセキュア)
        """
        form = schema.CardForm(formdata=self.request.params)
        if not form.validate():
            logger.debug("form error %s" % (form.errors,))
            # TODO: 入力エラー表示
            return dict()
        assert h.has_cart(self.request)
        cart = h.get_cart(self.request)

        # 変換
        order_id = cart.id
        card_number = form['card_number'].data
        exp_year = form['exp_year'].data
        exp_month = form['exp_month'].data
        order = self.request.session['order']
        order.update(
            order_no=order_id,
            card_holder_name=self.request.params['card_holder_name'],
            card_number=card_number,
            exp_year=exp_year,
            exp_month=exp_month,
        )
        self.request.session['order'] = order
        enrol = multicheckout_api.secure3d_enrol(self.request, order_id, card_number, exp_year, exp_month, cart.total_amount)
        if enrol.is_enable_auth_api():
            return dict(form=m_h.secure3d_acs_form(self.request, self.request.route_url('cart.secure3d_result'), enrol))
        elif enrol.is_enable_secure3d():
            # セキュア3D認証エラーだが決済APIを利用可能
            logger.debug("3d secure is failed ErrorCd = %s RetCd = %s" %(enrol.ErrorCd, enrol.RetCd))

        else:
            # セキュア3D認証エラー
            logger.debug("3d secure is failed ErrorCd = %s RetCd = %s" %(enrol.ErrorCd, enrol.RetCd))
            pass

    @view_config(route_name='cart.secure3d_result', request_method="POST", renderer="carts/confirm.html")
    def card_info_secure3d_callback(self):
        """ カード情報入力(3Dセキュア)コールバック
        3Dセキュア認証結果取得
        """
        assert h.has_cart(self.request)
        cart = h.get_cart(self.request)

        order = self.request.session['order']
        # 変換
        order_id = str(cart.id) + "00"
        pares = multicheckout_api.get_pares(self.request)
        md = multicheckout_api.get_md(self.request)
        order['pares'] = pares
        order['md'] = md
        order['order_id'] = order_id

        auth_result = multicheckout_api.secure3d_auth(self.request, order_id, pares, md)
        item_name = h.get_item_name(self.request, cart.performance)

        checkout_auth_result = multicheckout_api.checkout_auth_secure3d(
            self.request, order_id,
            item_name, cart.total_amount, 0, order['client_name'], order['mail_address'],
            order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
            mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
            eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
        )
        tran = dict(
            mvn=auth_result.Mvn, xid=auth_result.Xid, ts=auth_result.Ts,
            eci=auth_result.Eci, cavv=auth_result.Cavv, cavv_algorithm=auth_result.Cavva,
        )
        order['tran'] = tran
        self.request.session['order'] = order

        #auth_result = dict(OrderNo=checkout_auth_result.OrderNo, Status=checkout_auth_result.Status,
        #    PublicTranId=checkout_auth_result.PublicTranId, AheadComCd=checkout_auth_result.AheadComCd,
        #    ApprovalNo=checkout_auth_result.ApprovalNo, CardErrorCd=checkout_auth_result.CardErrorCd,
        #    ReqYmd=checkout_auth_result.ReqYmd, CmnErrorCd=checkout_auth_result.CmnErrorCd, )

        #logger.debug("%s" % auth_result)

        openid = authenticated_user(self.request)
        user = h.get_or_create_user(self.request, openid['clamed_id'])
        DBSession.add(checkout_auth_result)

        return dict(cart=cart, auth_result=checkout_auth_result)


    def multi_checkout(self):
        """ マルチ決済APIで決済確定
        """

class ConfirmView(object):
    """ 決済確認画面 """
    def __init__(self, request):
        self.request = request

    @view_config(route_name='payment.confirm', request_method="GET", renderer="carts/confirm.html")
    def get(self):

        assert h.has_cart(self.request)
        cart = h.get_cart(self.request)

        return dict(cart=cart)

    @view_config(route_name='payment.confirm', request_method="POST", renderer="carts/confirm.html")
    def get(self):

        assert h.has_cart(self.request)
        cart = h.get_cart(self.request)

        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.id==payment_delivery_pair_id
        ).one()
        raise HTTPFound(self.request.route_url("payment.finish"))


class CompleteView(object):
    """ 決済完了画面"""
    def __init__(self, request):
        self.request = request
        # TODO: Orderを表示？

    @view_config(route_name='payment.finish', request_method="POST", renderer="carts/completion.html")
    def __call__(self):
        assert h.has_cart(self.request)
        cart = h.get_cart(self.request)
        order_session = self.request.session['order']

        payment_delivery_pair_id = order_session['payment_delivery_pair_id']
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.id==payment_delivery_pair_id
        ).one()

        if payment_delivery_pair.payment_method_id == 3:
            # カード決済
            order = self.finish_payment_card(cart, order_session)
            DBSession.add(order)

        if payment_delivery_pair.delivery_method_id == 3:
            self.finish_reserved_number(cart, order_session)

        # 配送
        return dict(order=order)

    def finish_reserved_number(self, cart, order_session):
        # 窓口引き換え番号
        return plugins.create_reserved_number(self.request, cart)

    # TODO: APIに移動
    def finish_payment_card(self, cart, order):
        # 変換
        order_id = order['order_id']
        pares = order['pares']
        md = order['md']
        tran = order['tran']
        item_name = h.get_item_name(self.request, cart.performance)

        checkout_sales_result = multicheckout_api.checkout_sales_secure3d(
            self.request, order_id,
            item_name, cart.total_amount, 0, order['client_name'], order['mail_address'],
            order['card_number'], order['exp_year'] + order['exp_month'], order['card_holder_name'],
            mvn=tran['mvn'], xid=tran['xid'], ts=tran['ts'],
            eci=tran['eci'], cavv=tran['cavv'], cavv_algorithm=tran['cavv_algorithm'],
        )

        DBSession.add(checkout_sales_result)
        openid = authenticated_user(self.request)
        user = h.get_or_create_user(self.request, openid['clamed_id'])

        order = o_models.Order.create_from_cart(cart)
        order.multicheckout_approval_no = checkout_sales_result.ApprovalNo
        order.user = user
        cart.finish()

        return order
