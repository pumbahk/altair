# -*- coding: utf-8 -*-

import unittest
import re
from decimal import Decimal
from datetime import datetime, timedelta
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.models import (
            DBSession,
            Organization,
            OrganizationSetting,
            Event,
            Performance,
            Site,
            Venue,
            SalesSegmentGroup,
            SalesSegment,
            PaymentMethod,
            DeliveryMethod,
            PaymentDeliveryMethodPair,
            DateCalculationBase,
            PaymentMethodPlugin,
            DeliveryMethodPlugin
)

from altair.app.ticketing.orders.models import (
            Order,
            OrderedProduct,
            OrderedProductItem,
            OrderedProductItemToken
)

from altair.app.ticketing.payments import plugins as _payment_plugins

from . import orgs_with_rakuten
from .commands import RecordError
from .commands import (
    build_org_id_as_list,
    lookup_for_point_granted_order
)

test_org_code = ["RT", "VK", "RE", "XX", "BB"]
test_org_sn = ["RT", "VK", "eagles", "XX", "BB"]
test_point_type = [1, 1, 1, 0, None]

order_nos = ['0000000001', '0000000002', '0000000003']

class CommandTest(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db(modules=[
            "altair.app.ticketing.lots.models",
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.orders.models",
        ])

        self.orgs_with_rakuten = orgs_with_rakuten

        for i, (code, short_name, point_type) in enumerate(zip(test_org_code, test_org_sn, test_point_type)):
            self._build_test_data_per_org(i+1, code, short_name, point_type)

        DBSession.flush()

    def tearDown(self):
        _teardown_db()

    def _makeOrg(self, org_id, code, short_name, point_type):
        OrgSet = OrganizationSetting()
        OrgSet.point_type = point_type
        OrgSet.organization = Organization(id=org_id, code=code, short_name=short_name)

        return OrgSet

    def _makeEvent(self, organization):
        return Event(organization=organization, title=u'イベント')

    def _makePerformance(self, organization, event):
        import string, random
        return Performance(
            start_on=datetime(2017, 1, 1),
            end_on=datetime.now() - timedelta(days=3),
            event=event,
            name=u'パフォーマンス',
            code=organization.code + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            )

    def _build_test_data_per_org(self, org_id, code, short_name, point_type):

        orgset = self._makeOrg(org_id, code, short_name, point_type)
        org = orgset.organization
        event = self._makeEvent(org)
        sales_segment_group = SalesSegmentGroup(event=event)
        performance = self._makePerformance(org, event)

        OrganizationSetting.add(orgset)
        Performance.add(performance)

        p, d = self._build_payment_delivery_methods(org)
        pdmps = self._create_payment_delivery_method_pair(sales_segment_group=sales_segment_group, payment_methods=p, delivery_methods=d)

        for i, order_no in enumerate(order_nos):
            payment_plugin_id = None
            delivery_plugin_id = None

            if i == 1:
                delivery_plugin_id = _payment_plugins.CHECKOUT_PAYMENT_PLUGIN_ID

            order = self._create_order(str(org.code) + order_no, pdmps, payment_plugin_id, delivery_plugin_id, performance, org.id)

            Order.add(order)

    def _build_payment_delivery_methods(self, organization):
        payment_methods = {}
        delivery_methods = {}
        for attr_name in dir(_payment_plugins):
            g = re.match(ur'^(.*)_PAYMENT_PLUGIN_ID$', attr_name)
            if g:

                id = getattr(_payment_plugins, attr_name)
                name = g.group(1)

                pyament_plugin = PaymentMethodPlugin.get(id)

                if not pyament_plugin:
                    pyament_plugin = PaymentMethodPlugin(id=id, name=name)

                payment_methods[id] = \
                    PaymentMethod(
                        name=name, fee=Decimal(0.),
                        organization=organization,
                        payment_plugin_id=id,
                        _payment_plugin=pyament_plugin
                    )
            else:
                g = re.match(ur'^(.*)_DELIVERY_PLUGIN_ID$', attr_name)
                if g:

                    id = getattr(_payment_plugins, attr_name)
                    name = g.group(1)

                    delivery_plugin = DeliveryMethodPlugin.get(id)

                    if not delivery_plugin:
                        delivery_plugin = DeliveryMethodPlugin(id=id, name=name)

                    delivery_methods[id] = \
                        DeliveryMethod(
                            name=name,
                            fee_per_order=Decimal(0.),
                            fee_per_principal_ticket=Decimal(0.),
                            fee_per_subticket=Decimal(0.),
                            organization=organization,
                            delivery_plugin_id=id,
                            _delivery_plugin=delivery_plugin
                        )

        return payment_methods, delivery_methods

    def _create_payment_delivery_method_pair(self,
                    sales_segment_group,
                    system_fee=0.,
                    system_fee_type=0,
                    transaction_fee=0.,
                    delivery_fee_per_order=0.,
                    delivery_fee_per_principal_ticket=0.,
                    delivery_fee_per_subticket=0.,
                    special_fee=0,
                    special_fee_type=0,
                    discount=0.,
                    discount_unit=0,
                    payment_methods=None,
                    delivery_methods=None):

        return [
            PaymentDeliveryMethodPair(
                sales_segment_group=sales_segment_group,
                system_fee=Decimal(system_fee),
                system_fee_type=system_fee_type,
                transaction_fee=Decimal(transaction_fee),
                delivery_fee_per_order=Decimal(delivery_fee_per_order),
                delivery_fee_per_principal_ticket=Decimal(delivery_fee_per_principal_ticket),
                delivery_fee_per_subticket=Decimal(delivery_fee_per_subticket),
                special_fee=Decimal(special_fee),
                special_fee_type=special_fee_type,
                discount=Decimal(discount),
                discount_unit=discount_unit,
                public=True,
                payment_method=payment_method,
                delivery_method=delivery_method,
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=3,
                issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                issuing_interval_days=5,
                issuing_end_day_calculation_base=DateCalculationBase.OrderDate.v,
                issuing_end_in_days=364,
            )
            for payment_method in payment_methods.values()
            for delivery_method in delivery_methods.values()
        ]

    def _create_order(self, order_no, pdmps, payment_plugin_id = None, delivery_plugin_id=None, performance=None, org_id=None):
        import random
        if payment_plugin_id:
            pdmps = [pdmp for pdmp in pdmps if pdmp.payment_method.payment_plugin_id == payment_plugin_id]

        if delivery_plugin_id:
            pdmps = [pdmp for pdmp in pdmps if pdmp.delivery_method.delivery_plugin_id == delivery_plugin_id]
        else:
            pdmps = [pdmp for pdmp in pdmps if pdmp.delivery_method.delivery_plugin_id == _payment_plugins.CHECKOUT_PAYMENT_PLUGIN_ID]


        pdmp = random.choice(pdmps)

        system_fee = Decimal()
        special_fee = Decimal()
        transaction_fee = Decimal(pdmp and pdmp.transaction_fee or 0.)
        delivery_fee = Decimal(pdmp and pdmp.delivery_fee or 0.)
        special_fee = Decimal(special_fee)
        total_amount = Decimal(transaction_fee + delivery_fee + special_fee + Decimal(100.))

        order = Order(
            order_no = order_no,
            total_amount=total_amount,
            system_fee=system_fee,
            transaction_fee=transaction_fee,
            delivery_fee=delivery_fee,
            special_fee=special_fee,
            payment_delivery_pair=pdmp,
            performance=performance,
            organization_id=org_id
        )

        return order

    def test_build_org_id_as_list(self):
        organization = Organization.get(1)
        org_ids = build_org_id_as_list(organization)
        self.assertEquals(len(org_ids), 2)
        self.assertEquals(1 in org_ids, True)
        self.assertEquals(2 in org_ids, True)
        self.assertEquals(3 in org_ids, False)
        self.assertEquals(4 in org_ids, False)
        self.assertEquals(5 in org_ids, False)

    def test_lookup_for_point_granted_order(self):
        order_no = 'RT0000000001'
        organization = Organization.get(1)
        order = lookup_for_point_granted_order(order_no, organization)
        self.assertEqual(order.order_no, order_no)

    def test_lookup_for_point_granted_order_not_rakuten(self):
        order_no = 'RE0000000001'
        organization = Organization.get(3)
        order = lookup_for_point_granted_order(order_no, organization)
        self.assertEqual(order.order_no, order_no)

    # ヴィッセル（with_rakutenの中にあるorg）の予約は楽天チケットのorgで取得できることを確認
    def test_lookup_for_point_granted_order_with_rakuten(self):
        order_no = 'VK0000000001'
        organization = Organization.get(1)
        order = lookup_for_point_granted_order(order_no, organization)

        self.assertEqual(order.order_no, order_no)

    # with_rakutenの中にないorgの予約は楽天チケットのorgで取得されないことを確認
    def test_lookup_for_point_granted_order_without_rakuten(self):
        order_no = 'RE0000000001'
        organization = Organization.get(1)
        with self.assertRaises(RecordError):
            lookup_for_point_granted_order(order_no, organization)