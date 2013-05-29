# -*- coding:utf-8 -*-
import logging
from ticketing.core.api import get_channel
from .models import Cart, CartedProduct, CartedProductItem
from .api import is_quantity_only
from .exceptions import CartCreationException
from .stocker import InvalidProductSelectionException

logger = logging.getLogger(__name__)

class CartFactory(object):
    def __init__(self, request):
        self.request = request

    def create_cart(self, performance_id, seats, ordered_products):
        logger.debug('create cart for ordered products %s' % ordered_products)
        request = self.request
        # Cart
        # ここでシステム利用料を確定させるのはおかしいので、後の処理で上書きする
        channel = get_channel(request=request)
        cart = Cart.create(performance_id=performance_id, channel=channel.v,
                           browserid=getattr(request, 'browserid', None))
        for ordered_product, quantity in ordered_products:
            logger.debug("carted product for product_id=%s" % (ordered_product.id))
            # CartedProduct
            cart_product = CartedProduct(cart=cart, product=ordered_product, quantity=quantity)
            for ordered_product_item in ordered_product.items:
                # CartedProductItem
                if str(ordered_product_item.performance_id) != str(performance_id):
                    logger.debug("invalid product selection: performance_id does not match")
                    raise InvalidProductSelectionException
                subtotal_quantity = quantity * ordered_product_item.quantity
                logger.debug("carted product item for product_item_id=%s, performance_id=%s, quantity=%d" % (ordered_product_item.id, ordered_product_item.performance_id, subtotal_quantity))
                cart_product_item = CartedProductItem(
                    carted_product=cart_product,
                    quantity=subtotal_quantity,
                    product_item=ordered_product_item)

                logger.debug('stock_id %s, stock_type %s' % (ordered_product_item.stock.id, ordered_product_item.stock.stock_type_id))
                if is_quantity_only(ordered_product_item.stock):
                    # 数受けはここまでで処理完了
                    logger.debug('stock %d quantity only' % ordered_product_item.stock.id)
                    continue

                # 席割り当て
                item_seats = self.pop_seats(ordered_product_item, subtotal_quantity, seats)
                cart_product_item.seats = item_seats
    
        assert len(seats) == 0
        return cart
    
    
    def pop_seats(self, product_item, quantity, seats):
        """ product_itemに対応した席を取り出す
        """
    
        logger.debug("seat stocks = %s" % [s.stock_id for s in seats])
        my_seats = [seat for seat in seats if seat.stock_id == product_item.stock_id][:quantity]
        if len(my_seats) != quantity:
            logger.error("stock %d, quantity error %d != %d" % (product_item.stock_id, len(my_seats), quantity))
            raise CartCreationException
        map(seats.remove, my_seats)
        return my_seats
