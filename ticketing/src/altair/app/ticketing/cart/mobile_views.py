# -*- coding:utf-8 -*-
""" モバイルの商品選択までのビュー
"""

import logging
import re
import transaction

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

import sqlalchemy as sa

from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.core import api as c_api
#from altair.mobile.interfaces import IMobileRequest
from altair.app.ticketing.cart.selectable_renderer import selectable_renderer
from altair.app.ticketing.models import DBSession
from .reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from .stocker import NotEnoughStockException

from . import api
from . import helpers as h
from . import schemas
from .view_support import IndexViewMixin, get_amount_without_pdmp, get_seat_type_dicts
from .resources import PerformanceOrientedTicketingCartResource
from .exceptions import (
    NoEventError,
    NoPerformanceError,
    NoSalesSegment,
    InvalidCSRFTokenException, 
    OverQuantityLimitError, 
    ZeroQuantityError, 
    CartCreationException,
    TooManyCartsCreated,
)
from .views import limitter

logger = logging.getLogger(__name__)


@view_defaults(renderer=selectable_renderer('%(membership)s/mobile/index.html'), xhr=False, permission="buy", request_type='altair.mobile.interfaces.IMobileRequest')
class MobileIndexView(IndexViewMixin):
    """モバイルのパフォーマンス選択
    """
    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.prepare()

    @view_config(route_name='cart.index')
    def event_based_landing_page(self):
        logger.debug('mobile index')
        self.check_redirect(mobile=True)

        try:
            performance_id = long(self.request.params.get('pid') or self.request.params.get('performance'))
        except (ValueError, TypeError):
            performance_id = None

        try:
            sales_segment = self.context.sales_segment
        except NoSalesSegment:
            sales_segment = None

        preferred_performance = None

        if sales_segment is None:
            # パフォーマンスIDから販売区分の解決を試みる
            if performance_id:
                # performance_id で指定される Performance は
                # available_sales_segments に関連するものでなければならない

                sales_segments = self.context.available_sales_segments
                # 数が少ないのでリニアサーチ
                for _sales_segment in sales_segments:
                    if _sales_segment.performance_id == performance_id:
                        # 複数個の SalesSegment が該当する可能性があるが
                        # 最初の 1 つを採用することにする。実用上問題ない。
                        sales_segment = _sales_segment
                        break
                if sales_segment is None:
                    # 該当する物がない
                    preferred_performance = c_models.Performance.query.filter_by(id=performance_id, public=True).first()
                    if preferred_performance is not None:
                        if preferred_performance.event_id != self.context.event.id:
                            preferred_performance = None 

        if sales_segment is not None:
            return HTTPFound(self.request.route_url(
                    "cart.seat_types",
                    event_id=self.context.event.id,
                    performance_id=sales_segment.performance_id,
                    sales_segment_id=sales_segment.id))


        selector_name = c_api.get_organization(self.request).setting.performance_selector
        performance_selector = api.get_performance_selector(self.request, selector_name)
        key_to_formatted_sales_segments_map = performance_selector()

        # キー (公演名) が指定されている場合は、（日時、会場）のリスト
        key = self.request.params.get('key') or self.request.params.get('performance_name')
        if key:
            key_to_formatted_sales_segments_map = [(k, v) for k, v in key_to_formatted_sales_segments_map if k == key]
            if not key_to_formatted_sales_segments_map:
                return HTTPFound(self.request.route_url('cart.index', event_id=self.context.event.id))

        return dict(
            event=self.context.event,
            key_to_formatted_sales_segments_map=key_to_formatted_sales_segments_map,
            key=key,
            selector_label_1=performance_selector.label,
            selector_label_2=performance_selector.second_label,
            preferred_performance=preferred_performance
            )


    @view_config(route_name='cart.index2')
    def performance_based_landing_page(self):
        logger.debug('mobile index')
        self.check_redirect(mobile=True)

        try:
            sales_segment = self.context.sales_segment
        except NoSalesSegment:
            sales_segment = None

        if sales_segment is None:
            # performance_id で指定される Performance は
            # available_sales_segments に関連するものでなければならない

            for _sales_segment in self.context.available_sales_segments:
                if _sales_segment.performance_id == self.context.performance.id:
                    sales_segment = _sales_segment
            if sales_segment is None:
                raise NoPerformanceError('performance (%d) is not associated to the relevant SalesSegment' % self.context.performance.id)

        if sales_segment is not None:
            return HTTPFound(self.request.route_url(
                    "cart.seat_types2",
                    event_id=self.context.event.id,
                    performance_id=sales_segment.performance_id,
                    sales_segment_id=sales_segment.id))


        selector_name = c_api.get_organization(self.request).setting.performance_selector
        performance_selector = api.get_performance_selector(self.request, selector_name)
        key_to_formatted_sales_segments_map = performance_selector()

        return dict(
            event=self.context.event,
            key_to_formatted_sales_segments_map=key_to_formatted_sales_segments_map,
            selector_label_1=performance_selector.label,
            selector_label_2=performance_selector.second_label,
            preferred_performance=None
            )

@view_defaults(renderer=selectable_renderer('%(membership)s/mobile/seat_types.html'), xhr=False, request_type='altair.mobile.interfaces.IMobileRequest')
class MobileSelectSeatTypeView(object):
    """モバイルの商品選択
    """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='cart.seat_types')
    def seat_type(self):
        selector_name = c_api.get_organization(self.request).setting.performance_selector
        performance_selector = api.get_performance_selector(self.request, selector_name)

        try:
            seat_type_id = long(self.request.params.get('seat_type_id') or self.request.params.get('stid'))
        except (ValueError, TypeError):
            seat_type_id = None

        if seat_type_id:
            return HTTPFound(self.request.route_url(
                "cart.products",
                event_id=self.context.sales_segment.performance.event.id,
                performance_id=self.context.sales_segment.performance.id,
                sales_segment_id=self.context.sales_segment.id,
                seat_type_id=seat_type_id))

        sales_segment = self.context.sales_segment
        seat_type_dicts = get_seat_type_dicts(self.request, sales_segment)

        data = dict(
            seat_types=[
                dict(
                    products_url=self.request.route_url(
                        'cart.products',
                        event_id=self.request.context.event.id,
                        performance_id=sales_segment.performance.id,
                        sales_segment_id=sales_segment.id,
                        seat_type_id=_dict['id']),
                    **_dict
                    )
                for _dict in seat_type_dicts
                ],
            event=self.context.event,
            performance=sales_segment.performance,
            venue=sales_segment.performance.venue,
            sales_segment=sales_segment,
            return_value=performance_selector.select_value(sales_segment)
            )
        return data

    @view_config(route_name='cart.seat_types2')
    def seat_type2(self):
        selector_name = c_api.get_organization(self.request).setting.performance_selector
        performance_selector = api.get_performance_selector(self.request, selector_name)

        try:
            seat_type_id = long(self.request.params.get('seat_type_id') or self.request.params.get('stid'))
        except (ValueError, TypeError):
            seat_type_id = None

        if seat_type_id:
            return HTTPFound(self.request.route_url(
                "cart.products2",
                event_id=self.context.sales_segment.performance.event.id,
                performance_id=self.context.sales_segment.performance.id,
                sales_segment_id=self.context.sales_segment.id,
                seat_type_id=seat_type_id))

        sales_segment = self.context.sales_segment
        seat_type_dicts = get_seat_type_dicts(self.request, sales_segment)

        data = dict(
            seat_types=[
                dict(
                    products_url=self.request.route_url(
                        'cart.products2',
                        event_id=self.request.context.event.id,
                        performance_id=sales_segment.performance.id,
                        sales_segment_id=sales_segment.id,
                        seat_type_id=_dict['id']),
                    **_dict
                    )
                for _dict in seat_type_dicts
                ],
            event=self.context.event,
            performance=sales_segment.performance,
            venue=sales_segment.performance.venue,
            sales_segment=sales_segment,
            return_value=performance_selector.select_value(sales_segment)
            )
        return data

@view_defaults(renderer=selectable_renderer('%(membership)s/mobile/products.html'), xhr=False, request_type='altair.mobile.interfaces.IMobileRequest')
class MobileSelectProductView(object):
    """モバイルの商品選択
    """

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
        :return: list of tuple(altair.app.ticketing.products.models.Product, int)
        """

        controls = list(self.iter_ordered_items())
        logger.debug('order %s' % controls)
        if len(controls) == 0:
            return []

        products = dict([(p.id, p) for p in DBSession.query(c_models.Product).filter(c_models.Product.id.in_([c[0] for c in controls]))])
        logger.debug('order %s' % products)

        return [(products.get(int(c[0])), c[1]) for c in controls]

    @view_config(route_name='cart.products')
    @view_config(route_name='cart.products2')
    def products(self):
        seat_type_id = self.request.matchdict['seat_type_id']

        # 席種(イベントとパフォーマンスにひもづいてること)
        segment_stocks = DBSession.query(c_models.ProductItem.stock_id).filter(
            c_models.ProductItem.product_id==c_models.Product.id).filter(
            c_models.Product.sales_segment_id==self.context.sales_segment.id).filter(
            c_models.Product.public==True)

        seat_type = DBSession.query(c_models.StockType).filter(
            c_models.Performance.id==self.context.sales_segment.performance.id).filter(
            c_models.Performance.event_id==c_models.StockHolder.event_id).filter(
            c_models.StockHolder.id==c_models.Stock.stock_holder_id).filter(
            c_models.Stock.stock_type_id==c_models.StockType.id).filter(
            c_models.Stock.id.in_(segment_stocks)).filter(
            c_models.StockType.id==seat_type_id).first()

        if seat_type is None:
            raise NoEventError("No such seat_type (%s)" % seat_type_id)

        # 商品一覧
        products = DBSession.query(c_models.Product, c_models.StockStatus.quantity) \
            .join(c_models.Product.items) \
            .join(c_models.ProductItem.stock) \
            .join(c_models.Stock.stock_status) \
            .filter(c_models.Stock.stock_type_id==seat_type_id) \
            .filter(c_models.Product.sales_segment_id==self.context.sales_segment.id) \
            .filter(c_models.Product.public==True) \
            .filter(c_models.ProductItem.deleted_at == None) \
            .filter(c_models.Stock.deleted_at == None) \
            .order_by(sa.desc("Product.display_order, Product.price"))

        # CSRFトークン発行
        form = schemas.CSRFSecureForm(csrf_context=self.request.session)

        product_dicts = get_seat_type_dicts(self.request, self.context.sales_segment, seat_type.id)[0]['products']

        if isinstance(self.context, PerformanceOrientedTicketingCartResource):
            back_url = self.request.route_url('cart.seat_types2', performance_id=self.context.performance.id, sales_segment_id=self.context.sales_segment.id)
        else:
            back_url = self.request.route_url('cart.seat_types', event_id=self.context.event.id, sales_segment_id=self.context.sales_segment.id)
        return dict(
            event=self.context.event,
            performance=self.context.sales_segment.performance,
            venue=self.context.sales_segment.performance.venue,
            sales_segment=self.context.sales_segment,
            seat_type=seat_type,
            products=product_dicts,
            form=form,
            back_url=back_url
        )

    @limitter.acquire
    @view_config(route_name='cart.products', request_method="POST")
    @view_config(route_name='cart.products2', request_method="POST")
    def products_form(self):
        """商品の値検証とおまかせ座席確保とカート作成
        """
        performance_id = self.request.params.get('performance_id')
        seat_type_id = self.request.params.get('seat_type_id')
        sales_segment_group_id = self.request.matchdict["sales_segment_id"]

        # 古いカートを削除
        old_cart = api.get_cart(self.request) # これは get_cart でよい
        if old_cart:
            limitter._release(self.request)
            # !!! ここでトランザクションをコミットする !!!
            old_cart.release()
            api.remove_cart(self.request)
            transaction.commit()

        # セールスセグメント必須
        sales_segment = c_models.SalesSegment.filter_by(id=sales_segment_group_id).first()
        if sales_segment is None:
            raise NoEventError("No matching sales_segment")

        # パフォーマンス
        performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id).first()
        if performance is None:
            raise NoEventError("No such performance (%d)" % performance_id)

        # CSRFトークンの確認
        form = schemas.CSRFSecureForm(
            formdata=self.request.params,
            csrf_context=self.request.session)
        if not form.validate():
            raise InvalidCSRFTokenException

        # セッションからCSRFトークンを削除して再利用不可にしておく
        if 'csrf' in self.request.session:
            del self.request.session['csrf']
            self.request.session.persist()

        order_items = self.ordered_items

        # 購入枚数の制限
        sum_quantity = 0
        for product, quantity in order_items:
            sum_quantity += quantity * product.get_quantity_power(product.seat_stock_type, product.performance_id)
        logger.debug('sum_quantity=%s' % sum_quantity)
        if sum_quantity > sales_segment.upper_limit:
            raise OverQuantityLimitError(sales_segment.upper_limit)

        if sum_quantity == 0:
            raise ZeroQuantityError

        try:
            # カート生成(席はおまかせ)
            cart = api.order_products(
                self.request,
                sales_segment.id,
                order_items)
            cart.sales_segment = sales_segment
            if cart is None:
                transaction.abort()
                raise CartCreationException.from_resource(self.context, self.request)
        except NotEnoughAdjacencyException as e:
            transaction.abort()
            logger.debug("not enough adjacency")
            raise e
        except InvalidSeatSelectionException as e:
            # モバイルだとここにはこないかも
            transaction.abort()
            logger.debug("seat selection is invalid.")
            raise e
        except NotEnoughStockException as e:
            transaction.abort()
            logger.debug("not enough stock quantity.")
            raise e

        DBSession.add(cart)
        DBSession.flush()
        api.set_cart(self.request, cart)
        # 購入確認画面へ
        query = { 'seat_type_id': seat_type_id }
        if isinstance(self.context, PerformanceOrientedTicketingCartResource):
            query['performance_id'] = performance_id
        else:
            query['event_id'] = performance.event_id

        return HTTPFound(self.request.route_url('cart.order', sales_segment_id=sales_segment.id, _query=query))

@view_defaults(route_name='cart.order', request_method="GET", renderer=selectable_renderer('%(membership)s/mobile/reserve.html'), request_type='altair.mobile.interfaces.IMobileRequest')
class MobileReserveView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config()
    def reserve_mobile(self):
        cart = self.request.context.cart

        # XXX: ここ汚い. performance_id が与えられていなかったら /perforamnce/{performance_id} に戻るようにしている
        performance_id = None
        try:
            performance_id = long(self.request.params.get('performance_id'))
        except (ValueError, TypeError):
            pass

        event_id = None
        try:
            event_id = self.request.params.get('event_id')
        except (ValueError, TypeError):
            pass

        seat_type_id = None
        try:
            seat_type_id = self.request.params.get('seat_type_id')
        except (ValueError, TypeError):
            pass

        sales_segment_id = self.context.sales_segment.id

        performance = c_models.Performance.query.filter(c_models.Performance.id==performance_id).first()
        if performance:
            event = performance.event
            back_url = self.request.route_url('cart.products2', performance_id=performance.id, seat_type_id=seat_type_id,sales_segment_id=sales_segment_id)
        else:
            event = c_models.Event.query.filter(c_models.Event.id==event_id).one()
            back_url = self.request.route_url('cart.products', event_id=event.id, seat_type_id=seat_type_id,sales_segment_id=sales_segment_id)

        data = dict(
            event=event,
            sales_segment_id=sales_segment_id, 
            payment_url=self.request.route_url("cart.payment", sales_segment_id=sales_segment_id),
            cart=dict(
                products=[
                    dict(
                        name=p.product.name,
                        detail=h.product_name_with_unit(p.product.items),
                        quantity=p.quantity,
                        price=int(p.product.price),
                        seats=p.seats if p.product.sales_segment.seat_choice else [],
                        seat_quantity=p.seat_quantity
                        )
                    for p in cart.products
                    ],
                total_amount=h.format_number(get_amount_without_pdmp(cart)),
                ),
            back_url=back_url
            )
        return data
