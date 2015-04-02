# encoding: utf-8

import unittest
import mock
import itertools
from decimal import Decimal
from pyramid import testing
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.testing import _setup_db, _teardown_db

class DummyPaymentDeliveryPlugin(object):
    def validate_order(self, request, order_like, update=False):
        return

class DummyPaymentPlugin(object):
    def validate_order(self, request, order_like, update=False):
        return


class DummyDeliveryPlugin(object):
    def validate_order(self, request, order_like, update=False):
        return


class SaveOrderModificationTestBase(unittest.TestCase, CoreTestMixin):
    __test__ = False

    # --- modify_data の構造 ---
    # {
    #     'performance_id': 1,
    #     'sales_segment_id': 1,
    #     'transaction_fee': 0,
    #     'delivery_fee': 0,
    #     'system_fee': 0,
    #     'special_fee': 0,
    #     'total_amount': 0,
    #     'items': [
    #         {
    #             'id': 1,
    #             'product_id': 1,
    #             'quantity': 1,
    #             'price': 0,
    #             'elements': [
    #                 {
    #                     'id': 1,
    #                     'product_item': {
    #                         'id': 1,
    #                         'name': '',
    #                         'price': 0,
    #                         'quantity': 1,
    #                         'stock_holder_name': '',
    #                         'stock_type_id': 0,
    #                         'is_seat': False,
    #                         'quantity_only': False,
    #                         },
    #                     'product_item_id': 0, # これは new でサポート
    #                     'quantity': 1,
    #                     'price': 0, # これは new でサポート
    #                     'seats': [
    #                         {
    #                             'id': 1, # 実は l0_id
    #                             'l0_id': 1, # 実は l0_id、これは new でサポート
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             }
    #         ]
    #     }

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _pick_seats(self, stock, quantity):
        from altair.app.ticketing.core.models import SeatStatusEnum
        assert stock in self.stocks
        assert not stock.stock_type.quantity_only

        result = []
        for seat in self.seats:
            if seat.stock == stock and seat.status == SeatStatusEnum.Vacant.v:
                result.append(seat)
                if len(result) == quantity:
                    break
        else:
            assert False, 'len(result) < quantity (%d < %d)' % (len(result), quantity)
        return result

    def setUp(self):
        from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment, OrganizationSetting
        from altair.app.ticketing.cart.models import CartSetting
        self.request = testing.DummyRequest()
        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.lots.models',
                'altair.app.ticketing.orders.models',
                ]
            )
        CoreTestMixin.setUp(self)
        self.cart_settings = [
            CartSetting(organization=self.organization, name=u'default'),
            CartSetting(organization=self.organization, name=u'second'),
            ]
        for cart_setting in self.cart_settings:
            self.session.add(cart_setting)
        self.organization.settings = [
            OrganizationSetting(cart_setting=self.cart_settings[0]),
            ]
        self.stock_types = self._create_stock_types(4)
        self.stocks = self._create_stocks(self.stock_types, 10)
        self.seats = self._create_seats(self.stocks)
        self.sales_segment_group = SalesSegmentGroup(event=self.event)
        self.payment_delivery_method_pairs = self._create_payment_delivery_method_pairs(self.sales_segment_group)
        self.sales_segment = SalesSegment(sales_segment_group=self.sales_segment_group, payment_delivery_method_pairs=self.payment_delivery_method_pairs)
        self.products = self._create_products(self.stocks)
        self.config = testing.setUp(settings={
            'altair.cart.completion_page.temporary_store.cookie_name': 'xxx',
            'altair.cart.completion_page.temporary_store.secret': 'xxx',
            })
        self.config.include('altair.app.ticketing.cart.setup_components')

        patches = []
        patch = mock.patch('altair.app.ticketing.orders.api.refresh_order')
        patches.append(patch)
        self._refresh_order = patch.start()
        patch = mock.patch('altair.app.ticketing.orders.api.lookup_plugin')
        patches.append(patch)
        self._lookup_plugin = patch.start()
        self._lookup_plugin.return_value = [DummyPaymentDeliveryPlugin(), DummyPaymentPlugin(), DummyDeliveryPlugin()]
        self.patches = patches

    def tearDown(self):
        for patch in self.patches:
            patch.stop()
        testing.tearDown()
        _teardown_db()

    def test_identity_old_data_structure(self):
        from altair.app.ticketing.orders.models import Order
        order = self._create_order([
            (self.products[0], 2),
            ],
            self.sales_segment,
            self.payment_delivery_method_pairs[0]
            )
        self.session.add(order)
        self.session.flush()
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements), 1)
        self.assertEqual(order.items[0].elements[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements[0].seats), 2)
        modify_data = {
            'performance_id': self.performance.id,
            'sales_segment_id': self.sales_segment.id,
            'transaction_fee': 0,
            'delivery_fee': 0,
            'system_fee': 0,
            'special_fee': None,
            'total_amount': order.total_amount,
            'ordered_products': [
                {
                    'id': order.items[0].id,
                    'product_id': order.items[0].product_id,
                    'quantity': order.items[0].quantity,
                    'price': order.items[0].price,
                    'ordered_product_items': [
                        {
                            'id': order.items[0].elements[0].id,
                            'product_item': {
                                'id': order.items[0].elements[0].product_item.id,
                                'price': order.items[0].elements[0].product_item.price,
                                },
                            'quantity': order.items[0].elements[0].quantity,
                            'seats': [
                                {
                                    'id': order.items[0].elements[0].seats[0].l0_id
                                    },
                                {
                                    'id': order.items[0].elements[0].seats[1].l0_id
                                    }
                                ],
                            }
                        ]
                    }
                ]
            }
        modified_order, warnings = self._callFUT(self.request, order, modify_data)
        self.assertTrue(len(warnings) == 0)
        self.assertTrue(self._refresh_order.called_with_arguments(modified_order))
        self.assertEqual(modified_order.order_no, order.order_no)
        self.assertEqual(modified_order.branch_no, order.branch_no + 1)
        self.assertEqual(modified_order.cart_setting_id, order.cart_setting_id)
        self.assertEqual(len(modified_order.items), 1)
        self.assertEqual(modified_order.items[0].quantity, 2)
        self.assertEqual(len(modified_order.items[0].elements), 1)
        self.assertEqual(modified_order.items[0].elements[0].quantity, 2)
        self.assertEqual(modified_order.items[0].elements[0].seats, order.items[0].elements[0].seats)

    def test_identity(self):
        from altair.app.ticketing.orders.models import Order
        order = self._create_order([
            (self.products[0], 2),
            ],
            self.sales_segment,
            self.payment_delivery_method_pairs[0]
            )
        self.session.add(order)
        self.session.flush()
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements), 1)
        self.assertEqual(order.items[0].elements[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements[0].seats), 2)
        modify_data = {
            'performance_id': self.performance.id,
            'sales_segment_id': self.sales_segment.id,
            'transaction_fee': 0,
            'delivery_fee': 0,
            'system_fee': 0,
            'special_fee': None,
            'total_amount': order.total_amount,
            'items': [
                {
                    'id': order.items[0].id,
                    'product_id': order.items[0].product_id,
                    'quantity': order.items[0].quantity,
                    'price': order.items[0].price,
                    'elements': [
                        {
                            'id': order.items[0].elements[0].id,
                            'product_item_id': order.items[0].elements[0].product_item.id,
                            'quantity': order.items[0].elements[0].quantity,
                            'price': order.items[0].elements[0].price,
                            'seats': [
                                {
                                    'id': order.items[0].elements[0].seats[0].l0_id
                                    },
                                {
                                    'id': order.items[0].elements[0].seats[1].l0_id
                                    }
                                ],
                            }
                        ]
                    }
                ]
            }
        modified_order, warnings = self._callFUT(self.request, order, modify_data)
        self.assertTrue(len(warnings) == 0)
        self.assertTrue(self._refresh_order.called_with_arguments(modified_order))
        self.assertEqual(modified_order.order_no, order.order_no)
        self.assertEqual(modified_order.branch_no, order.branch_no + 1)
        self.assertEqual(modified_order.cart_setting_id, order.cart_setting_id)
        self.assertEqual(len(modified_order.items), 1)
        self.assertEqual(modified_order.items[0].quantity, 2)
        self.assertEqual(len(modified_order.items[0].elements), 1)
        self.assertEqual(modified_order.items[0].elements[0].quantity, 2)
        self.assertEqual(modified_order.items[0].elements[0].seats, order.items[0].elements[0].seats)

    def test_removal(self):
        from altair.app.ticketing.orders.models import Order
        order = self._create_order([
            (self.products[0], 2),
            ],
            self.sales_segment,
            self.payment_delivery_method_pairs[0]
            )
        self.session.add(order)
        self.session.flush()
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements), 1)
        self.assertEqual(order.items[0].elements[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements[0].seats), 2)
        modify_data = {
            'performance_id': self.performance.id,
            'sales_segment_id': self.sales_segment.id,
            'transaction_fee': 0,
            'delivery_fee': 0,
            'system_fee': 0,
            'special_fee': None,
            'total_amount': self.products[0].price * 1,
            'items': [
                {
                    'id': order.items[0].id,
                    'product_id': order.items[0].product_id,
                    'quantity': 1,
                    'price': order.items[0].price,
                    'elements': [
                        {
                            'id': order.items[0].elements[0].id,
                            'product_item_id': order.items[0].elements[0].product_item.id,
                            'quantity': 1,
                            'price': order.items[0].elements[0].price,
                            'seats': [
                                {
                                    'id': order.items[0].elements[0].seats[0].l0_id
                                    },
                                ],
                            }
                        ]
                    }
                ]
            }
        modified_order, warnings = self._callFUT(self.request, order, modify_data)
        self.assertTrue(len(warnings) == 0)
        self.assertTrue(self._refresh_order.called_with_arguments(modified_order))
        self.assertEqual(modified_order.order_no, order.order_no)
        self.assertEqual(modified_order.branch_no, order.branch_no + 1)
        self.assertEqual(modified_order.cart_setting_id, order.cart_setting_id)
        self.assertEqual(len(modified_order.items), 1)
        self.assertEqual(modified_order.items[0].quantity, 1)
        self.assertEqual(len(modified_order.items[0].elements), 1)
        self.assertEqual(modified_order.items[0].elements[0].quantity, 1)
        self.assertTrue(set(modified_order.items[0].elements[0].seats) < set(order.items[0].elements[0].seats))

    def test_removal_with_zero_quantity(self):
        from altair.app.ticketing.orders.models import Order
        order = self._create_order([
            (self.products[0], 2),
            (self.products[1], 1),
            ],
            self.sales_segment,
            self.payment_delivery_method_pairs[0]
            )
        self.session.add(order)
        self.session.flush()
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.items[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements), 1)
        self.assertEqual(order.items[0].elements[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements[0].seats), 2)
        modify_data = {
            'performance_id': self.performance.id,
            'sales_segment_id': self.sales_segment.id,
            'transaction_fee': 0,
            'delivery_fee': 0,
            'system_fee': 0,
            'special_fee': None,
            'total_amount': self.products[0].price * 1,
            'items': [
                {
                    'id': order.items[0].id,
                    'product_id': order.items[0].product_id,
                    'quantity': 1,
                    'price': order.items[0].price,
                    'elements': [
                        {
                            'id': order.items[0].elements[0].id,
                            'product_item_id': order.items[0].elements[0].product_item.id,
                            'quantity': 1,
                            'price': order.items[0].elements[0].price,
                            'seats': [
                                {
                                    'id': order.items[0].elements[0].seats[0].l0_id
                                    },
                                ],
                            }
                        ]
                    },
                {
                    'id': order.items[1].id,
                    'product_id': order.items[1].product_id,
                    'quantity': 0,
                    'price': order.items[1].price,
                    'elements': [
                        {
                            'id': order.items[1].elements[0].id,
                            'product_item_id': order.items[1].elements[0].product_item.id,
                            'quantity': 1,
                            'price': order.items[1].elements[0].price,
                            }
                        ]
                    }
                ]
            }
        modified_order, warnings = self._callFUT(self.request, order, modify_data)
        self.assertTrue(len(warnings) == 0)
        self.assertTrue(self._refresh_order.called_with_arguments(modified_order))
        self.assertEqual(modified_order.order_no, order.order_no)
        self.assertEqual(modified_order.branch_no, order.branch_no + 1)
        self.assertEqual(modified_order.cart_setting_id, order.cart_setting_id)
        self.assertEqual(len(modified_order.items), 1)
        self.assertEqual(modified_order.items[0].quantity, 1)
        self.assertEqual(len(modified_order.items[0].elements), 1)
        self.assertEqual(modified_order.items[0].elements[0].quantity, 1)
        self.assertTrue(set(modified_order.items[0].elements[0].seats) < set(order.items[0].elements[0].seats))

    def test_appending(self):
        from altair.app.ticketing.core.models import SeatStatusEnum
        from altair.app.ticketing.orders.models import Order
        order = self._create_order([
            (self.products[0], 2),
            ],
            self.sales_segment,
            self.payment_delivery_method_pairs[0]
            )
        self.session.add(order)
        self.session.flush()
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements), 1)
        self.assertEqual(order.items[0].elements[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements[0].seats), 2)
        prev_product_1_stock_status_quantity = self.products[3].items[0].stock.stock_status.quantity
        modify_data = {
            'performance_id': self.performance.id,
            'sales_segment_id': self.sales_segment.id,
            'transaction_fee': 0,
            'delivery_fee': 0,
            'system_fee': 0,
            'special_fee': None,
            'total_amount': self.products[0].price * 2 + self.products[3].price * 1,
            'items': [
                {
                    'id': order.items[0].id,
                    'product_id': self.products[0].id,
                    'quantity': order.items[0].quantity,
                    'price': self.products[0].price,
                    'elements': [
                        {
                            'id': order.items[0].elements[0].id,
                            'product_item_id': self.products[0].items[0].id,
                            'quantity': order.items[0].elements[0].quantity,
                            'price': self.products[0].items[0].price,
                            'seats': [
                                {
                                    'id': order.items[0].elements[0].seats[0].l0_id
                                    },
                                {
                                    'id': order.items[0].elements[0].seats[1].l0_id
                                    }
                                ],
                            }
                        ]
                    },
                {
                    'id': None,
                    'product_id': self.products[3].id,
                    'quantity': 1,
                    'price': self.products[3].price * 1,
                    'elements': [
                        {
                            'id': None,
                            'product_item_id': self.products[3].items[0].id,
                            'quantity': 1,
                            'price': self.products[3].items[0].price,
                            'seats': [
                                {
                                    'id': self._pick_seats(self.products[3].items[0].stock, 1)[0].l0_id,
                                    },
                                ],
                            }
                        ]
                    }
                ]
            }
        modified_order, warnings = self._callFUT(self.request, order, modify_data)
        self.assertTrue(len(warnings) == 0)
        self.assertTrue(self._refresh_order.called_with_arguments(modified_order))
        self.assertEqual(modified_order.order_no, order.order_no)
        self.assertEqual(modified_order.branch_no, order.branch_no + 1)
        self.assertEqual(modified_order.cart_setting_id, order.cart_setting_id)
        self.assertEqual(len(modified_order.items), 2)
        self.assertEqual(modified_order.items[0].quantity, 2)
        self.assertEqual(len(modified_order.items[0].elements), 1)
        self.assertEqual(modified_order.items[0].elements[0].quantity, 2)
        self.assertEqual([seat.l0_id for seat in modified_order.items[0].elements[0].seats], [seat.l0_id for seat in order.items[0].elements[0].seats])
        self.assertEqual(modified_order.items[1].quantity, 1)
        self.assertEqual(len(modified_order.items[1].elements), 1)
        self.assertEqual(modified_order.items[1].elements[0].quantity, 1)
        self.assertEqual(len(modified_order.items[1].elements[0].seats), 1)
        self.assertEqual(modified_order.items[1].elements[0].seats[0].stock, self.products[3].items[0].stock)
        self.assertEqual(prev_product_1_stock_status_quantity - self.products[3].items[0].stock.stock_status.quantity, 1)


class SaveOrderModificationOldTest(SaveOrderModificationTestBase):
    __test__ = True
    def _getTarget(self):
        from .api import save_order_modification_old
        return save_order_modification_old

class SaveOrderModificationNewTest(SaveOrderModificationTestBase):
    __test__ = True
    def _getTarget(self):
        from .api import save_order_modification_new
        return save_order_modification_new

    @mock.patch('altair.app.ticketing.orders.api.logger')
    def test_zero_principal_product(self, logger):
        from altair.app.ticketing.orders.exceptions import OrderCreationError
        from altair.app.ticketing.orders.models import Order
        order = self._create_order([
            (self.products[0], 2),
            (self.products[1], 1),
            ],
            self.sales_segment,
            self.payment_delivery_method_pairs[0]
            )
        self.session.add(order)
        self.session.flush()
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.items[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements), 1)
        self.assertEqual(order.items[0].elements[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements[0].seats), 2)
        self.assertEqual(order.items[1].quantity, 1)
        self.assertEqual(len(order.items[1].elements), 1)
        self.assertEqual(order.items[1].elements[0].quantity, 1)
        self.assertEqual(len(order.items[1].elements[0].seats), 0)
        modify_data = {
            'performance_id': self.performance.id,
            'sales_segment_id': self.sales_segment.id,
            'transaction_fee': 0,
            'delivery_fee': 0,
            'system_fee': 0,
            'special_fee': None,
            'total_amount': 0,
            'items': [
                {
                    'id': order.items[0].id,
                    'product_id': order.items[0].product_id,
                    'quantity': order.items[0].quantity,
                    'price': 0,
                    'elements': [
                        {
                            'id': order.items[0].elements[0].id,
                            'product_item_id': order.items[0].elements[0].product_item.id,
                            'quantity': order.items[0].elements[0].quantity,
                            'price': 0,
                            'seats': [
                                {
                                    'id': order.items[0].elements[0].seats[0].l0_id
                                    },
                                {
                                    'id': order.items[0].elements[0].seats[1].l0_id
                                    }
                                ],
                            }
                        ]
                    },
                {
                    'id': order.items[1].id,
                    'product_id': order.items[1].product_id,
                    'quantity': order.items[1].quantity,
                    'price': 0,
                    'elements': [
                        {
                            'id': order.items[1].elements[0].id,
                            'product_item_id': order.items[1].elements[0].product_item.id,
                            'quantity': order.items[1].elements[0].quantity,
                            'price': 1,
                            'seats': None
                            }
                        ]
                    }
                ]
            }
        modified_order, warnings = self._callFUT(self.request, order, modify_data)
        self.assertEqual(
            [warning.interpolate() for warning in warnings],
            [
                u'商品「A」の価格が0に設定されています',
                u'商品「A」の商品明細「product_item_of_A」の価格が0に設定されています',
                u'商品「B」の価格が0に設定されています',
                u'商品「B」の商品明細の価格の合計が商品の価格と一致しません (1 ≠ 0)',
                ]
            )

    def test_appending_with_insufficient_stock(self):
        from altair.app.ticketing.core.models import SeatStatusEnum
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.orders.exceptions import OrderCreationError
        order = self._create_order([
            (self.products[0], 2),
            ],
            self.sales_segment,
            self.payment_delivery_method_pairs[0]
            )
        self.session.add(order)
        self.session.flush()
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements), 1)
        self.assertEqual(order.items[0].elements[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements[0].seats), 2)
        prev_product_1_stock_status_quantity = self.products[3].items[0].stock.stock_status.quantity
        modify_data = {
            'performance_id': self.performance.id,
            'sales_segment_id': self.sales_segment.id,
            'transaction_fee': 0,
            'delivery_fee': 0,
            'system_fee': 0,
            'special_fee': None,
            'total_amount': self.products[0].price * 2 + self.products[3].price * 1,
            'items': [
                {
                    'id': order.items[0].id,
                    'product_id': self.products[0].id,
                    'quantity': order.items[0].quantity,
                    'price': self.products[0].price,
                    'elements': [
                        {
                            'id': order.items[0].elements[0].id,
                            'product_item_id': self.products[0].items[0].id,
                            'quantity': order.items[0].elements[0].quantity,
                            'price': self.products[0].items[0].price,
                            'seats': [
                                {
                                    'id': order.items[0].elements[0].seats[0].l0_id
                                    },
                                {
                                    'id': order.items[0].elements[0].seats[1].l0_id
                                    }
                                ],
                            }
                        ]
                    },
                {
                    'id': None,
                    'product_id': self.products[1].id,
                    'quantity': 100,
                    'price': self.products[1].price * 1,
                    'elements': [
                        {
                            'id': None,
                            'product_item_id': self.products[1].items[0].id,
                            'quantity': 100,
                            'price': self.products[1].items[0].price,
                            }
                        ]
                    }
                ]
            }
        with self.assertRaises(OrderCreationError) as c:
            modified_order, warnings = self._callFUT(self.request, order, modify_data)

        self.assertEqual(c.exception.message, u'在庫がありません (席種: B, 個数: 100)')

    def test_appending_with_insufficient_adjacency(self):
        from altair.app.ticketing.core.models import SeatStatusEnum
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.orders.exceptions import OrderCreationError
        order = self._create_order([
            (self.products[0], 2),
            ],
            self.sales_segment,
            self.payment_delivery_method_pairs[0]
            )
        self.session.add(order)
        self.session.flush()
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements), 1)
        self.assertEqual(order.items[0].elements[0].quantity, 2)
        self.assertEqual(len(order.items[0].elements[0].seats), 2)
        prev_product_1_stock_status_quantity = self.products[3].items[0].stock.stock_status.quantity
        modify_data = {
            'performance_id': self.performance.id,
            'sales_segment_id': self.sales_segment.id,
            'transaction_fee': 0,
            'delivery_fee': 0,
            'system_fee': 0,
            'special_fee': None,
            'total_amount': self.products[0].price * 2 + self.products[3].price * 1,
            'items': [
                {
                    'id': order.items[0].id,
                    'product_id': self.products[0].id,
                    'quantity': order.items[0].quantity,
                    'price': self.products[0].price,
                    'elements': [
                        {
                            'id': order.items[0].elements[0].id,
                            'product_item_id': self.products[0].items[0].id,
                            'quantity': order.items[0].elements[0].quantity,
                            'price': self.products[0].items[0].price,
                            'seats': [
                                {
                                    'id': order.items[0].elements[0].seats[0].l0_id
                                    },
                                {
                                    'id': order.items[0].elements[0].seats[1].l0_id
                                    }
                                ],
                            }
                        ]
                    },
                {
                    'id': None,
                    'product_id': self.products[3].id,
                    'quantity': 5,
                    'price': self.products[3].price * 1,
                    'elements': [
                        {
                            'id': None,
                            'product_item_id': self.products[3].items[0].id,
                            'quantity': 5,
                            'price': self.products[3].items[0].price,
                            }
                        ]
                    }
                ]
            }
        with self.assertRaises(OrderCreationError) as c:
            modified_order, warnings = self._callFUT(self.request, order, modify_data)

        self.assertEqual(c.exception.message, u'配席可能な座席がありません (席種: D, 個数: 5)')

class GetRefundPerOrderFeeTest(unittest.TestCase):
    def _getTarget(self):
        from .api import get_refund_per_order_fee
        return get_refund_per_order_fee

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _build_dummy_order(self):
        return testing.DummyModel(
            payment_delivery_pair=testing.DummyModel(
                transaction_fee_per_order=Decimal(11),
                delivery_fee_per_order=Decimal(5),
                transaction_fee_per_ticket=Decimal(13),
                delivery_fee_per_ticket=Decimal(17)
                ),
            system_fee=Decimal(13),
            transaction_fee=Decimal(17),
            delivery_fee=Decimal(19),
            special_fee=Decimal(23),
            refund_system_fee=Decimal(13),
            refund_transaction_fee=Decimal(17),
            refund_delivery_fee=Decimal(19),
            refund_special_fee=Decimal(23),
            items=[
                testing.DummyModel(
                    price=Decimal(13),
                    quantity=1,
                    elements=[
                        testing.DummyModel(
                            price=Decimal(7),
                            quantity=1,
                            refund_price=Decimal(7),
                            product_item_id=1,
                            product_item=testing.DummyModel(
                                id=1,
                                price=Decimal(5),
                                ticket_bundle_id=1
                                )
                            ),
                        testing.DummyModel(
                            price=Decimal(3),
                            quantity=2,
                            refund_price=Decimal(3),
                            product_item_id=2,
                            product_item=testing.DummyModel(
                                id=2,
                                price=Decimal(13),
                                ticket_bundle_id=None
                                )
                            ),
                        ]
                    )
                ]
            )


    def test_get_refund_per_order_fee_1(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(0))

    def test_get_refund_per_order_fee_2(self):
        refund = testing.DummyModel(
            include_system_fee=True,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(13))

    def test_get_refund_per_order_fee_3(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=True,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(11))

    def test_get_refund_per_order_fee_4(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=True,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(5))

    def test_get_refund_per_order_fee_5(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=True,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(23))

    def test_get_refund_per_order_fee_6(self):
        refund = testing.DummyModel(
            include_system_fee=True,
            include_transaction_fee=True,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(24))

    def test_get_refund_per_order_fee_7(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=True,
            include_delivery_fee=True,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(16))

    def test_get_refund_per_order_fee_8(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=True,
            include_special_fee=True,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(28))

    def test_get_refund_per_order_fee_9(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=True
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(6))

    def test_get_refund_per_order_fee_10(self):
        refund = testing.DummyModel(
            include_system_fee=True,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=True
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(19))

class GetRefundPerTicketFeeTest(unittest.TestCase):
    def _getTarget(self):
        from .api import get_refund_per_ticket_fee
        return get_refund_per_ticket_fee

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _build_dummy_order(self):
        return testing.DummyModel(
            payment_delivery_pair=testing.DummyModel(
                transaction_fee_per_order=Decimal(11),
                delivery_fee_per_order=Decimal(5),
                transaction_fee_per_ticket=Decimal(13),
                delivery_fee_per_ticket=Decimal(17)
                ),
            system_fee=Decimal(13),
            transaction_fee=Decimal(17),
            delivery_fee=Decimal(19),
            special_fee=Decimal(23),
            refund_system_fee=Decimal(13),
            refund_transaction_fee=Decimal(17),
            refund_delivery_fee=Decimal(19),
            refund_special_fee=Decimal(23),
            items=[
                testing.DummyModel(
                    price=Decimal(13),
                    quantity=1,
                    elements=[
                        testing.DummyModel(
                            price=Decimal(7),
                            quantity=1,
                            refund_price=Decimal(7),
                            product_item_id=1,
                            product_item=testing.DummyModel(
                                id=1,
                                price=Decimal(5),
                                ticket_bundle_id=1
                                )
                            ),
                        testing.DummyModel(
                            price=Decimal(3),
                            quantity=2,
                            refund_price=Decimal(3),
                            product_item_id=2,
                            product_item=testing.DummyModel(
                                id=2,
                                price=Decimal(13),
                                ticket_bundle_id=None
                                )
                            ),
                        ]
                    )
                ]
            )

    def test_get_refund_per_ticket_fee_1(self):
        refund = testing.DummyModel(
            include_system_fee=True,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(0))

    def test_get_refund_per_ticket_fee_2(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=True,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(13))

    def test_get_refund_per_ticket_fee_3(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=True,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(17))

    def test_get_refund_per_ticket_fee_4(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=True,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(0))

class GetRefundTicketPrice(unittest.TestCase):
    def _getTarget(self):
        from .api import get_refund_ticket_price
        return get_refund_ticket_price

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _build_dummy_order(self):
        return testing.DummyModel(
            payment_delivery_pair=testing.DummyModel(
                transaction_fee_per_order=Decimal(11),
                delivery_fee_per_order=Decimal(5),
                transaction_fee_per_ticket=Decimal(13),
                delivery_fee_per_ticket=Decimal(17)
                ),
            system_fee=Decimal(13),
            transaction_fee=Decimal(17),
            delivery_fee=Decimal(19),
            special_fee=Decimal(23),
            refund_system_fee=Decimal(13),
            refund_transaction_fee=Decimal(17),
            refund_delivery_fee=Decimal(19),
            refund_special_fee=Decimal(23),
            items=[
                testing.DummyModel(
                    price=Decimal(13),
                    quantity=1,
                    elements=[
                        testing.DummyModel(
                            price=Decimal(7),
                            quantity=1,
                            refund_price=Decimal(7),
                            product_item_id=1,
                            product_item=testing.DummyModel(
                                id=1,
                                price=Decimal(5),
                                ticket_bundle_id=1
                                )
                            ),
                        testing.DummyModel(
                            price=Decimal(3),
                            quantity=2,
                            refund_price=Decimal(3),
                            product_item_id=2,
                            product_item=testing.DummyModel(
                                id=2,
                                price=Decimal(13),
                                ticket_bundle_id=None
                                )
                            ),
                        ]
                    )
                ]
            )

    def test_get_refund_ticket_price_1(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order, 1)
        self.assertEqual(result, Decimal(0))

    def test_get_refund_ticket_price_2(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order, 2)
        self.assertEqual(result, Decimal(0))

    def test_get_refund_ticket_price_3(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order, 3)
        self.assertEqual(result, Decimal(0))

    def test_get_refund_ticket_price_4(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=True
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order, 1)
        self.assertEqual(result, Decimal(7))

    def test_get_refund_ticket_price_5(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=True,
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order, 2)
        self.assertEqual(result, Decimal(3))

    def test_get_refund_ticket_price_6(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=True
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order, 3)
        self.assertEqual(result, Decimal(0))


class GetOrderByIdTest(unittest.TestCase):
    def _getTarget(self):
        from .api import get_order_by_id
        return get_order_by_id

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.lots.models',
                'altair.app.ticketing.orders.models',
                ]
            )
        self.request = testing.DummyRequest()

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _make_order(self, order_no, branch_no, id=None, **kwargs):
        from .models import Order
        return Order(
            id=id,
            order_no=order_no,
            branch_no=branch_no,
            total_amount=0,
            transaction_fee=0,
            delivery_fee=0,
            system_fee=0,
            special_fee=0,
            **kwargs
            )

    def test_no_branches(self):
        order = self._make_order(id=1, order_no='a', branch_no=1)
        self.session.add(order)
        self.session.flush()
        result = self._callFUT(self.request, 1)
        self.assertEqual(order, result)

    def test_branches(self):
        branches = [
            self._make_order(id=1, order_no='a', branch_no=1),
            self._make_order(id=2, order_no='a', branch_no=2),
            self._make_order(id=3, order_no='a', branch_no=3)
            ]
        for order in branches:
            self.session.add(order)
        self.session.flush()
        for order in branches:
            result = self._callFUT(self.request, order.id)
            self.assertEqual(branches[2], result)

    def test_branches_deleted(self):
        from datetime import datetime
        branches = [
            self._make_order(id=1, order_no='a', branch_no=1),
            self._make_order(id=2, order_no='a', branch_no=2),
            self._make_order(id=3, order_no='a', branch_no=3, deleted_at=datetime.now())
            ]
        for order in branches:
            self.session.add(order)
        self.session.flush()
        for order in branches:
            result = self._callFUT(self.request, order.id, include_deleted=False)
            self.assertEqual(branches[1], result)

        for order in branches:
            result = self._callFUT(self.request, order.id, include_deleted=True)
            self.assertEqual(branches[2], result)

class CallPaymentDeliveryPluginTest(unittest.TestCase):
    def setUp(self):
        self.lookup_plugin_patch = mock.patch('altair.app.ticketing.orders.api.lookup_plugin')
        self.lookup_plugin = self.lookup_plugin_patch.start()

    def tearDown(self):
        self.lookup_plugin_patch.stop()

    def _getTarget(self):
        from .api import call_payment_delivery_plugin
        return call_payment_delivery_plugin

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_pd_available(self):
        request = mock.Mock()
        order_like = mock.Mock(
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=1
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=1
                    )
                )
            )
        self.lookup_plugin.return_value = [mock.Mock(), mock.Mock(), mock.Mock()]
        self._callFUT(request, order_like)

        self.lookup_plugin.called_once_with(request, order_like.payment_delivery_pair)
        self.lookup_plugin.return_value[0].finish2.called_one_with(request, order_like)
        self.assertFalse(self.lookup_plugin.return_value[1].finish2.called)
        self.assertFalse(self.lookup_plugin.return_value[2].finish2.called)

    def test_ordinary_p_d(self):
        request = mock.Mock()
        order_like = mock.Mock(
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=1
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=1
                    )
                )
            )
        self.lookup_plugin.return_value = [None, mock.Mock(), mock.Mock()]
        self._callFUT(request, order_like)

        self.lookup_plugin.assert_called_once_with(request, order_like.payment_delivery_pair)
        self.lookup_plugin.return_value[1].finish2.assert_called_one_with(request, order_like)
        self.lookup_plugin.return_value[2].finish2.assert_called_one_with(request, order_like)

    def test_exclusion(self):
        request = mock.Mock()
        order_like = mock.Mock(
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=1
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=1
                    )
                )
            )
        self.lookup_plugin.return_value = [None, mock.Mock(), mock.Mock()]
        self._callFUT(request, order_like, excluded_payment_plugin_ids=[1])
        self.lookup_plugin.assert_called_once_with(request, order_like.payment_delivery_pair)
        self.assertFalse(self.lookup_plugin.return_value[1].finish2.called)
        self.lookup_plugin.return_value[2].finish2.assert_called_one_with(request, order_like)

    def test_inclusion1(self):
        request = mock.Mock()
        order_like = mock.Mock(
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=1
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=1
                    )
                )
            )
        self.lookup_plugin.return_value = [None, mock.Mock(), mock.Mock()]
        self._callFUT(request, order_like, included_payment_plugin_ids=[2])
        self.lookup_plugin.assert_called_once_with(request, order_like.payment_delivery_pair)
        self.assertFalse(self.lookup_plugin.return_value[1].finish2.called)
        self.lookup_plugin.return_value[2].finish2.assert_called_one_with(request, order_like)

    def test_inclusion2(self):
        request = mock.Mock()
        order_like = mock.Mock(
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=1
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=1
                    )
                )
            )
        self.lookup_plugin.return_value = [None, mock.Mock(), mock.Mock()]
        self._callFUT(request, order_like, included_payment_plugin_ids=[1])
        self.lookup_plugin.assert_called_once_with(request, order_like.payment_delivery_pair)
        self.lookup_plugin.return_value[1].finish2.assert_called_one_with(request, order_like)
        self.lookup_plugin.return_value[2].finish2.assert_called_one_with(request, order_like)

