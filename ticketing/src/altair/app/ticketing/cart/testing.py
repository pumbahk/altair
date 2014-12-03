#-*- coding: utf-8 -*-

class CartTestMixin(object):
    def _create_cart(self, product_quantity_pairs, sales_segment, cart_setting, pdmp=None):
        from .models import Cart, CartedProduct, CartedProductItem
        from altair.app.ticketing.core.models import SeatStatusEnum
        def mark_in_cart(seat):
            seat.status = SeatStatusEnum.InCart.v
            return seat
        return Cart(
            _order_no=self.new_order_no(),
            organization_id=self.organization.id,
            shipping_address=self._create_shipping_address(),
            sales_segment=sales_segment,
            payment_delivery_pair=pdmp,
            cart_setting=cart_setting,
            products=[
                CartedProduct(
                    product=product, quantity=quantity,
                    items=[
                        CartedProductItem(
                            product_item=product_item,
                            seats=[mark_in_cart(seat) for seat in self._pick_seats(product_item.stock, quantity * product_item.quantity)]
                            )
                        for product_item in product.items
                        ]
                    )
                for product, quantity in product_quantity_pairs
                ]
            )
