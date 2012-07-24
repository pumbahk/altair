# -*- coding:utf-8 -*-

from .models import Cart, CartedProduct, CartedProductItem, DBSession
from .api import get_system_fee

class CartFactory(object):
    def __init__(self, request):
        self.request = request

    def create_cart(self, performance_id, seats, ordered_products):
        request = self.request
        # Cart
        system_fee = get_system_fee(request)
        cart = Cart(performance_id=performance_id, system_fee=system_fee)
        for ordered_product, quantity in ordered_products:
            # CartedProduct
            cart_product = CartedProduct(cart=cart, product=ordered_product, quantity=quantity)
            for ordered_product_item in ordered_product.items:
                # CartedProductItem
                cart_product_item = CartedProductItem(carted_product=cart_product, quantity=quantity,
                    product_item=ordered_product_item)
                # 席割り当て
                if not ordered_product_item.stock.stock_type.quantity_only:
                    item_seats = self.pop_seats(ordered_product_item, quantity, seats)
                    cart_product_item.seats = item_seats
    
        assert len(seats) == 0
        return cart
    
    
    def pop_seats(self, product_item, quantity, seats):
        """ product_itemに対応した席を取り出す
        """
    
        my_seats = [seat for seat in seats if seat.stock_id == product_item.stock_id][:quantity]
        assert len(my_seats) == quantity
        map(seats.remove, my_seats)
        return my_seats
