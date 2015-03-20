# -*- coding:utf-8 -*-
import logging
from altair.app.ticketing.core.api import get_channel
from altair.app.ticketing.users.models import Membership
from .models import Cart, CartedProduct, CartedProductItem
from .api import is_quantity_only, get_membership
from .exceptions import CartCreationException
from .stocker import InvalidProductSelectionException

logger = logging.getLogger(__name__)

class CartFactory(object):
    def __init__(self, request):
        self.request = request

    def create_cart(self, sales_segment, seats, ordered_products, cart_setting=None, membership=None):
        logger.debug('create cart for ordered products %s' % ordered_products)
        request = self.request
        # Cart
        # ここでシステム利用料を確定させるのはおかしいので、後の処理で上書きする
        channel = get_channel(request=request)
        if cart_setting is None:
            cart_setting = getattr(getattr(self.request, 'context'), 'cart_setting', None)

        user = getattr(request, 'altair_auth_info', None)

        if user is not None and not sales_segment.applicable(user=user, type='all'):
            raise CartCreationException.from_resource(
                request.context,
                request,
                'user {0} is not associated to sales_segment_id({1})'.format(user, sales_segment.id)
                )

        if membership is None:
            if user is not None:
                membership = get_membership(user)
        if cart_setting is None:
            if membership is not None:
                cart_setting = membership.organization.setting.cart_setting
            else:
                cart_setting = sales_segment.sales_segment_group.event.organization.setting.cart_setting
        cart = Cart.create(
            self.request,
            sales_segment=sales_segment, 
            performance_id=sales_segment.performance_id,
            channel=int(channel),
            cart_setting_id=cart_setting.id,
            browserid=getattr(request, 'browserid', ''),
            user_agent=getattr(request, 'user_agent', ''),
            cart_session_id=getattr(request.session, 'id', ''),
            membership_id=membership and membership.id
            )

        for ordered_product, quantity in ordered_products:
            assert ordered_product.deleted_at is None
            logger.debug("carted product for product_id=%s" % (ordered_product.id))
            if ordered_product.sales_segment_id != sales_segment.id:
                logger.debug("invalid product selection: sales_segment_id does not match")
                raise InvalidProductSelectionException
            # CartedProduct
            cart_product = CartedProduct(cart=cart, product=ordered_product, quantity=quantity, organization_id=cart.organization_id)
            for ordered_product_item in ordered_product.items:
                assert ordered_product_item.deleted_at is None
                # 特定のパフォーマンスに紐づく販売区分の場合、
                # 商品明細に紐づく在庫のパフォーマンスと合致している必要がある
                if sales_segment.performance_id is not None and \
                   sales_segment.performance_id != ordered_product_item.stock.performance_id:
                    logger.debug("invalid product selection: product_item.stock.performance_id (%r) != sales_segment.performace_id (%r)" % (ordered_product_item.stock.performace_id, sales_segment.performance_id))
                subtotal_quantity = quantity * ordered_product_item.quantity
                logger.debug("carted product item for product_item_id=%s, stock_id=%s, stock.performance_id=%s, quantity=%d" % (ordered_product_item.id, ordered_product_item.stock_id, ordered_product_item.stock.performance_id, subtotal_quantity))
                cart_product_item = CartedProductItem(
                    carted_product=cart_product,
                    organization_id=cart_product.organization_id,
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
            raise CartCreationException.from_resource(
                self.request.context,
                self.request,
                "stock %d, quantity error %d != %d" % (product_item.stock_id, len(my_seats), quantity)
                )
        map(seats.remove, my_seats)
        return my_seats
