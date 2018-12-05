# -*- coding: utf-8 -*-
from datetime import datetime
import mock
from pyramid.testing import (
    setUp,
    tearDown,
    DummyModel,
    DummyRequest,
    )
from altair.app.ticketing.testing import (
    _setup_db,
    _teardown_db,
    )

from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.cart.testing import CartTestMixin


class FamiPortTestBase(CoreTestMixin, CartTestMixin):
    now = datetime(2013, 1, 1, 0, 0, 0)

    def setUp(self):
        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.cart.models',
                'altair.app.ticketing.lots.models',
                'altair.app.ticketing.orders.models',
                'altair.app.ticketing.users.models',
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.famiport.models',
                ]
            )
        from altair.app.ticketing.core.models import (
            CartMixin,
            DateCalculationBase
            )
        class DummyCart(DummyModel, CartMixin):
            pass

        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        self.pdmps = [
            DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_interval_days=None,
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=1,
                payment_due_at=None,
                payment_method=DummyModel(payment_plugin_id=1),
                delivery_method=DummyModel(delivery_plugin_id=1)
                ),
            DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_interval_days=None,
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=None,
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=1,
                payment_due_at=None,
                payment_method=DummyModel(payment_plugin_id=1),
                delivery_method=DummyModel(delivery_plugin_id=1)
                ),
            DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                issuing_interval_days=3,
                issuing_start_at=None,
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=1,
                payment_due_at=None,
                payment_method=DummyModel(payment_plugin_id=1),
                delivery_method=DummyModel(delivery_plugin_id=1)
                ),
            DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_interval_days=None,
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=3,
                payment_due_at=None,
                payment_method=DummyModel(payment_plugin_id=1),
                delivery_method=DummyModel(delivery_plugin_id=1)
                ),
            ]

        self.user = DummyModel()
        self.shipping_addresses = [
            DummyModel(
                user=self.user,
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=u'test2@test.com',
                prefecture=u'東京都',
                city=u'品川区',
                address_1=u'西五反田',
                address_2=u'いぇい',
                ),
            DummyModel(
                user=self.user,
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=None,
                prefecture=u'東京都',
                city=u'品川区',
                address_1=u'西五反田',
                address_2=u'いぇい',
                ),
            DummyModel(
                user=self.user,
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=None,
                email_2=u'test2@test.com',
                prefecture=u'東京都',
                city=u'品川区',
                address_1=u'西五反田',
                address_2=u'いぇい',
                ),
            DummyModel(
                user=self.user,
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=None,
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=u'test2@test.com',
                prefecture=u'東京都',
                city=u'品川区',
                address_1=u'西五反田',
                address_2=u'いぇい',
                ),
            DummyModel(
                user=self.user,
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=None,
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=u'test2@test.com',
                prefecture=u'東京都',
                city=u'品川区',
                address_1=u'西五反田',
                address_2=u'いぇい',
                ),
            DummyModel(
                user=self.user,
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=None,
                email_1=u'test1@test.com',
                email_2=u'test2@test.com',
                prefecture=u'東京都',
                city=u'品川区',
                address_1=u'西五反田',
                address_2=u'いぇい',
                ),
            ]

        self.famiport_tenant = DummyModel(
            playGuideId='',
            phoneInput=0,
            nameInput=0,
            code='001',
            )

        self.organization = DummyModel(
            id=99,
            code='XX',
            famiport_tenant=self.famiport_tenant,
            setting = DummyModel(i18n=False)
            )

        orders = []

        for ii, payment_delivery_pair in enumerate(self.pdmps):
            for jj, shipping_address in enumerate(self.shipping_addresses):
                operator = DummyModel()

                event = DummyModel(
                    title=u'event title日本語日本語日本語',
                    organization=self.organization,
                    organization_id=self.organization.id,
                    )

                performance = DummyModel(
                    event=event,
                    start_on=datetime(2013, 3, 1, 1, 2, 3),
                    end_on=datetime(2013, 3, 1, 2, 3, 4),
                    )

                sales_segment_group = DummyModel(
                    event=event,
                    organization_id=self.organization.id,
                    )

                sales_segment = DummyModel(
                    id=int(str(ii) + str(jj)),
                    event=performance.event,
                    performance=performance,
                    sales_segment_group=sales_segment_group,
                    )

                order_no = 'XX00000001'

                ordered_products = []

                for ii in range(5):
                    product_items = [
                        DummyModel(
                            ticket_bundle=DummyModel(
                                tickets=[
                                    DummyModel(
                                        ticket_format=DummyModel(
                                            delivery_methods=[
                                                payment_delivery_pair.delivery_method
                                                ]
                                            )
                                        )
                                    ]
                                )
                            )
                        for _ in range(0, 5)
                        ]
                    product = DummyModel(
                        num_tickets=mock.Mock(return_value=len(product_items)),
                        num_principal_tickets=mock.Mock(return_value=len(product_items)),
                        items=product_items
                        )
                    ordered_product = DummyModel(
                        product=product,
                        elements=[
                            DummyModel(
                                quantity=1,
                                product_item=product_item
                                )
                            for product_item in product_items
                            ],
                        )
                    ordered_products.append(ordered_product)

                cart = DummyCart(
                    organization_id=self.organization.id,
                    order_no=order_no,
                    performance=performance,
                    shipping_address=shipping_address,
                    payment_delivery_pair=payment_delivery_pair,
                    total_amount=1000,
                    point_amount=0,
                    payment_amount=1000,
                    system_fee=300,
                    transaction_fee=400,
                    delivery_fee=200,
                    special_fee_name=u'特別手数料',
                    special_fee=1,
                    channel=1,
                    cart_setting_id=1,
                    membership_id=None,
                    operator=operator,
                    sales_segment=sales_segment,
                    organization=self.organization,
                    created_at=self.now,
                    items=ordered_products,
                    finish=lambda *args, **kwds: mock.Mock()(*args, **kwds),
                    )
                order = DummyModel(
                    order_no=order_no,
                    shipping_address=shipping_address,
                    payment_delivery_pair=payment_delivery_pair,
                    total_amount=1000,
                    point_amount=0,
                    payment_amount=1000,
                    system_fee=300,
                    transaction_fee=400,
                    delivery_fee=200,
                    special_fee=1,
                    issuing_start_at=cart.issuing_start_at,
                    issuing_end_at=cart.issuing_end_at,
                    payment_start_at=cart.payment_start_at,
                    payment_due_at=cart.payment_due_at,
                    sales_segment=sales_segment,
                    organization=self.organization,
                    paid_at=(datetime.now() if ii % 2 else None),
                    cart=cart,
                    items=cart.items,
                    )
                orders.append(order)
        self.orders = orders

    def tearDown(self):
        tearDown()
        self.session.remove()
        _teardown_db()
