# -*- coding:utf-8 -*-

""" TBA
"""

import unittest
from pyramid import testing

class OrderTests(unittest.TestCase):
    def _getTarget(self):
        from . import models
        return models.Order

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_create_from_cart(self):

        from ..cart import models as c_models
        from ..core import models as core_models

        cart = c_models.Cart(
            products=[
                c_models.CartedProduct(
                    items=[
                        c_models.CartedProductItem(
                            product_item=core_models.ProductItem(price=100.00),
                        ),
                    ],
                    product=core_models.Product(
                        price=100.00,
                    ),
                    quantity=1,
                ),
            ],
        )

        target = self._getTarget()

        result = target.create_from_cart(cart)

        self.assertIsNotNone(result)
        self.assertEqual(len(result.ordered_products), 1)
        ordered_product = result.ordered_products[0]
        self.assertEqual(ordered_product.price, 100.00)
        self.assertEqual(len(ordered_product.ordered_product_items), 1)
        ordered_product_item = ordered_product.ordered_product_items[0]
        self.assertEqual(ordered_product_item.price, 100.00)