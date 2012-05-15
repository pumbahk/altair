# -*- coding:utf-8 -*-
from . import security
from pyramid.decorator import reify
from . import models as m

class TicketingCartResrouce(object):
    def __init__(self, request):
        self.request = request

    def acquire_product(self, product, amount):
        """ 商品確保
        """

        for product_item in product.items:
            self.acquire_product_item(product_item, amount)

    def has_stock(self, amount, product_item):
        return product_item.stock.quantity - m.CartedProduct.get_reserved_amount(product_item=product_item) > amount

    def acquire_product_item(self, product_item, amount):
        # 在庫チェック
        if not self.hash_stock(amount, product_item):
            raise Exception # TODO: 例外クラス定義

        self.cart.add_product_item(product_item, amount)

    @reify
    def cart_session_id(self):
        return security.cart_session_id(self.request)

    @reify
    def cart(self):
        return m.Cart.get_or_create(self.cart_session_id)
