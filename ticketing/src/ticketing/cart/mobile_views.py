# -*- coding:utf-8 -*-
""" モバイルの商品選択までのビュー
"""

import logging
import re
import transaction

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

import sqlalchemy as sa

from ticketing.core import models as c_models
from ticketing.core import api as c_api
#from altair.mobile.interfaces import IMobileRequest
from ticketing.cart.selectable_renderer import selectable_renderer
from ticketing.models import DBSession
from .reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from .stocker import NotEnoughStockException

from . import api
from . import helpers as h
from . import schemas
from .api import get_seat_type_triplets
from .view_support import IndexViewMixin
from .exceptions import (
    NoEventError,
    NoPerformanceError,
    NoSalesSegment,
    InvalidCSRFTokenException, 
    OverQuantityLimitError, 
    ZeroQuantityError, 
    CartCreationException,
)

logger = logging.getLogger(__name__)


class MobileIndexView(IndexViewMixin):
    """モバイルのパフォーマンス選択
    """
    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.prepare()

    @view_config(route_name='cart.index', renderer=selectable_renderer('carts_mobile/%(membership)s/index.html'), xhr=False, permission="buy", request_type='altair.mobile.interfaces.IMobileRequest')
    def __call__(self):
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

        if sales_segment is None:
            # パフォーマンスIDから販売区分の解決を試みる
            if performance_id:
                # performance_id で指定される Performance は
                # available_sales_segments に関連するものでなければならない

                for _sales_segment in self.context.available_sales_segments:
                    if _sales_segment.performance_id == performance_id:
                        sales_segment = _sales_segment
                if sales_segment is None:
                    raise NoPerformanceError(event_id=self.context.event_id)

        if sales_segment is not None:
            return HTTPFound(self.request.route_url(
                    "cart.seat_types",
                    event_id=self.context.event.id,
                    performance_id=performance_id,
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
            selector_label_2=performance_selector.second_label
            )


class MobileSelectProductView(object):
    """モバイルの商品選択
    """
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name='cart.seat_types', renderer=selectable_renderer('carts_mobile/%(membership)s/seat_types.html'), xhr=False, request_type='altair.mobile.interfaces.IMobileRequest')
    def __call__(self):
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

        seat_type_triplets = get_seat_type_triplets(self.context.sales_segment.id)

        data = dict(
            seat_types=[
                dict(
                    id=s.id,
                    name=s.name,
                    description=s.description,
                    style=s.style,
                    products_url=self.request.route_url('cart.products',
                                                        event_id=self.context.event.id,
                                                        performance_id=self.context.sales_segment.performance.id,
                                                        sales_segment_id=self.context.sales_segment.id, seat_type_id=s.id),
                    availability=available > 0,
                    availability_text=h.get_availability_text(available),
                    quantity_only=s.quantity_only,
                    )
                for s, total, available in seat_type_triplets
                ],
            event=self.context.event,
            performance=self.context.sales_segment.performance,
            venue=self.context.sales_segment.performance.venue,
            sales_segment=self.context.sales_segment,
            return_value=performance_selector.select_value(self.context.sales_segment)
            )
        return data

    @view_config(route_name='cart.products', renderer=selectable_renderer('carts_mobile/%(membership)s/products.html'), xhr=False, request_type='altair.mobile.interfaces.IMobileRequest')
    def products(self):
        logger.debug('cart.products')
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
        products = DBSession.query(c_models.Product) \
            .join(c_models.Product.items) \
            .join(c_models.ProductItem.stock) \
            .filter(c_models.Stock.stock_type_id==seat_type_id) \
            .filter(c_models.Product.sales_segment_id==self.context.sales_segment.id) \
            .filter(c_models.Product.public==True) \
            .order_by(sa.desc("Product.display_order, Product.price"))

        # CSRFトークン発行
        form = schemas.CSRFSecureForm(csrf_context=self.request.session)

        return dict(
            event=self.context.event,
            performance=self.context.sales_segment.performance,
            venue=self.context.sales_segment.performance.venue,
            sales_segment=self.context.sales_segment,
            seat_type=seat_type,
            upper_limit=self.context.sales_segment.upper_limit,
            products=[
                dict(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    detail=h.product_name_with_unit(product, self.context.sales_segment.performance.id),
                    price=h.format_number(product.price, ","),
                )
                for product in products
            ],
            form=form,
        )

class MobileReserveView(object):

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

    @view_config(route_name='cart.order', request_method="GET", renderer=selectable_renderer('carts_mobile/%(membership)s/reserve.html'), request_type='altair.mobile.interfaces.IMobileRequest')
    def reserve_mobile(self):
        cart = api.get_cart_safe(self.request)

        performance_id = self.request.params.get('performance_id')
        seat_type_id = self.request.params.get('seat_type_id')
        sales_segment_id = self.request.matchdict["sales_segment_id"]

        # セールスセグメント必須
        sales_segment = c_models.SalesSegment.filter_by(id=sales_segment_id).first()

        performance = c_models.Performance.query.filter(
            c_models.Performance.id==performance_id).first()
        if performance:
            event = performance.event
        else:
            event = None

        data = dict(
            event=event,
            performance=performance, 
            seat_type_id=seat_type_id,
            sales_segment_id=sales_segment_id, 
            payment_url=self.request.route_url("cart.payment", sales_segment_id=sales_segment.id),
            cart=dict(products=[dict(name=p.product.name, 
                                     quantity=p.quantity,
                                     price=int(p.product.price),
                                     seats=p.seats,
                                ) 
                                for p in cart.products],
                      total_amount=h.format_number(cart.tickets_amount),
            ))
        return data

    @view_config(route_name='cart.products', renderer=selectable_renderer('carts_mobile/%(membership)s/products.html'), xhr=False, request_type='altair.mobile.interfaces.IMobileRequest', request_method="POST")
    def products_form(self):
        """商品の値検証とおまかせ座席確保とカート作成
        """
        performance_id = self.request.params.get('performance_id')
        seat_type_id = self.request.params.get('seat_type_id')
        sales_segment_group_id = self.request.matchdict["sales_segment_id"]

        # 古いカートを削除
        old_cart = api.get_cart(self.request)
        if old_cart:
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
        sum_quantity = sum(num for product, num in order_items)
        logger.debug('sum_quantity=%s' % sum_quantity)
        if sum_quantity > sales_segment.upper_limit:
            raise OverQuantityLimitError(sales_segment.upper_limit)

        if sum_quantity == 0:
            raise ZeroQuantityError

        try:
            # カート生成(席はおまかせ)
            cart = api.order_products(
                self.request,
                performance_id,
                order_items)
            cart.sales_segment = sales_segment
            if cart is None:
                transaction.abort()
                logger.debug("cart is None. aborted.")
                raise CartCreationException
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
        query = dict(
            performance_id=performance_id,
            event_id=performance.event_id,
            seat_type_id=seat_type_id,
        )
        return HTTPFound(self.request.route_url('cart.order', sales_segment_id=sales_segment.id, _query=query))
