# -*- coding:utf-8 -*-
from pyramid.decorator import reify
from ticketing.products import models as p_models
from . import security
from . import models as m

class TicketingCartResrouce(object):
    def __init__(self, request):
        self.request = request

    def acquire_product(self, product, amount):
        """ 商品確保
        """

        for product_item in product.items:
            self.acquire_product_item(product_item, amount)

    def get_stock_status(self, product_item_id):
        """
        ProductItem -> Stock -> StockStatus
        :param product_item_id: プロダクトアイテムID
        :return: :class:`ticketing.products.models.StockStatus`
        """
        return m.DBSession.query(p_models.StockStatus).filter(
                p_models.ProductItem.id==product_item_id
            ).filter(
                p_models.ProductItem.stock_id==p_models.Stock.id
            ).filter(
                p_models.Stock.id==p_models.StockStatus.stock_id
            ).one()

    def has_stock(self, product_item_id, quantity):
        """在庫確認(Stock)
        :param product_item_id:
        :param quantity: 要求数量
        :return: bool
        """
        stock_status = self.get_stock_status(product_item_id=product_item_id)
        return stock_status.quantity >= quantity

    def acquire_product_item(self, product_item, amount):
        # 在庫チェック
        if not self.has_stock(amount, product_item):
            raise Exception # TODO: 例外クラス定義

        self.cart.add_product_item(product_item, amount)

    @reify
    def cart_session_id(self):
        return security.cart_session_id(self.request)

    @reify
    def cart(self):
        return m.Cart.get_or_create(self.cart_session_id)

    def convert_order_product_items(self, order_products):
        """ 選択したProductから必要なProductItemと個数にまとめる
        :param order_products: list of (product_id, quantity)
        :return: list of (product_item_id, quantity)
        """

    def take_seats_in_cart(self, seats):
        """  Seat状況更新(SeatStatus)
        """

    def select_seat(self, seat_type_id, quantity):
        """ 隣接座席で確保する(SeatAdjacency)
        """

    def order(self, order_items):
        """
        :param order_items: list of tuple(product_id, quantity)
        :returns: :class:`.models.Cart`
        """

        # SeatとProductItemとどちらで処理を進めるか検討 座席割当はSeatでないといけない
        seats = []
        # このループはSeatTypeであるべき
        for product_item_id, quantity in self.convert_order_product_items(order_items):
            if not self.has_stock(product_item_id, quantity):
                return False
            seats += self.select_seat(product_item_id, quantity)
        # TODO: Cart作成,CartedProductItemに座席割当(Cart,CartedProduct, CartedProductItem)
        self.take_seats_in_cart(seats)