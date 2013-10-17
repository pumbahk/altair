class CartTestMixin(object):
    def _create_cart(self, product_quantity_pairs, sales_segment, pdmp=None):
        from .models import Cart, CartedProduct, CartedProductItem
        from altair.app.ticketing.core.models import SeatStatusEnum

        return Cart(
            _order_no=self.new_order_no(),
            organization_id=self.organization.id,
            shipping_address=self._create_shipping_address(),
            sales_segment=sales_segment,
            payment_delivery_pair=pdmp,
            products=[
                CartedProduct(
                    product=product, quantity=quantity,
                    items=[
                        CartedProductItem(
                            product_item=product_item,
                            seats=list(self._pick_seats(product_item.stock, quantity * product_item.quantity))
                            )
                        for product_item in product.items
                        ]
                    )
                for product, quantity in product_quantity_pairs
                ]
            )

