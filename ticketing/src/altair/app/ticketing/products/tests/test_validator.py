# -*- coding:utf-8 -*-
import unittest
from pyramid.testing import DummyModel
from wtforms.validators import ValidationError
from altair.app.ticketing.core.models import (
    TicketBundle,
    Ticket,
    TicketFormat,
    SalesSegment,
    SalesSegmentGroup,
    PaymentDeliveryMethodPair,
    DeliveryMethod,
    DeliveryMethodPlugin
)
from altair.app.ticketing.payments import plugins
from ..formhelpers import validate_ticket_bundle_and_sales_segment_set
from altair.app.ticketing.testing import _setup_db

model_dependencies = [
    'altair.app.ticketing.models',
    'altair.app.ticketing.orders.models',
    'altair.app.ticketing.core.models',
    'altair.app.ticketing.users.models',
    'altair.app.ticketing.cart.models',
    'altair.app.ticketing.lots.models',
]

class ValidatorTests(unittest.TestCase):
    """
    販売区分の引取方法にコンビニがある場合、券面構成内にも
    該当するコンビニのものがあるべき
    """

    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(model_dependencies)

    def setUp(self):
        self.dummy_field1 = DummyModel(
            errors=[]
        )
        self.dummy_field2 = DummyModel(
            errors=[]
        )
        self.dummy_field3 = DummyModel(
            errors=[]
        )
        self.dummy_field4 = DummyModel(
            errors=[]
        )
        self.sej_delivery_method = DeliveryMethod(
            id=1,
            delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID
        )
        self.famiport_delivery_method = DeliveryMethod(
            id=2,
            delivery_plugin_id=plugins.FAMIPORT_DELIVERY_PLUGIN_ID
        )
        self.non_store_delivery_method = DeliveryMethod(
            id=3,
            delivery_plugin_id=plugins.SHIPPING_DELIVERY_PLUGIN_ID
        )
        self.pdmp_with_sej = PaymentDeliveryMethodPair(
            id=1,
            delivery_method=self.sej_delivery_method
        )
        self.pdmp_with_fami = PaymentDeliveryMethodPair(
            id=2,
            delivery_method=self.famiport_delivery_method
        )
        self.pdmp_without_store = PaymentDeliveryMethodPair(
            id=3,
            delivery_method=self.non_store_delivery_method
        )
        self.ticket_bundle_sej = TicketBundle(
            id=1,
            name=u'bundle_with_sej',
            tickets=[
                Ticket(
                    id=1,
                    name=u'sej_ticket',
                    flags=1,
                    filename=u'sej_ticket.svg',
                    cover_print=True,
                    visible=True,
                    ticket_format=TicketFormat(
                        id=1,
                        name=u'sej_format',
                        visible=False,
                        delivery_methods=[self.sej_delivery_method]
                    )
                )
            ]
        )
        self.ticket_bundle_fami = TicketBundle(
            id=2,
            name=u'bundle_with_fami',
            tickets=[
                Ticket(
                    id=2,
                    name=u'fami_ticket',
                    flags=1,
                    filename=u'fami_ticket.svg',
                    cover_print=True,
                    visible=True,
                    ticket_format=TicketFormat(
                        id=2,
                        name=u'fami_format',
                        visible=False,
                        delivery_methods=[self.famiport_delivery_method]
                    )
                )
            ]
        )
        self.ticket_bundle_both = TicketBundle(
            id=3,
            name=u'bundle_with_fami',
            tickets=[
                Ticket(
                    id=3,
                    name=u'sej_ticket',
                    flags=1,
                    filename=u'sej_ticket.svg',
                    cover_print=True,
                    visible=True,
                    ticket_format=TicketFormat(
                        id=1,
                        name=u'sej_format',
                        visible=False,
                        delivery_methods=[self.sej_delivery_method]
                    )
                ),
                Ticket(
                    id=4,
                    name=u'fami_ticket',
                    flags=1,
                    filename=u'fami_ticket.svg',
                    cover_print=True,
                    visible=True,
                    ticket_format=TicketFormat(
                        id=2,
                        name=u'fami_format',
                        visible=False,
                        delivery_methods=[self.famiport_delivery_method]
                    )
                )
            ]
        )
        self.ticket_bundle_non_store = TicketBundle(
            id=4,
            name=u'bundle_with_non_store',
            tickets=[
                Ticket(
                    id=5,
                    name=u'non_store_ticket',
                    flags=1,
                    filename=u'non_store_ticket.svg',
                    cover_print=True,
                    visible=True,
                    ticket_format=TicketFormat(
                        id=3,
                        name=u'non_store_format',
                        visible=False,
                        delivery_methods=[self.non_store_delivery_method]
                    )
                )
            ]
        )
        self.sales_segment_both_store_in = SalesSegment(
            id=1,
            payment_delivery_method_pairs=[
                self.pdmp_with_sej,
                self.pdmp_with_fami
            ]
        )
        self.sales_segment_non_store_in = SalesSegment(
            id=2,
            payment_delivery_method_pairs=[
                self.pdmp_without_store
            ]
        )
        self.sales_segment_sej_in = SalesSegment(
            id=3,
            payment_delivery_method_pairs=[
                self.pdmp_with_sej
            ]
        )
        self.sales_segment_fami_in = SalesSegment(
            id=4,
            payment_delivery_method_pairs=[
                self.pdmp_with_fami
            ]
        )

    def tearDown(self):
        pass

    def test_ticket_bundle_with_non_store_validation(self):
        """
        販売区分の引取方法にコンビニがあって、
        券面構成内にはコンビニがない場合は、
        validationに引っかかってfield.errorsにエラーメッセージが入る
        """
        validate_ticket_bundle_and_sales_segment_set(
            field=self.dummy_field1,
            sales_segment=self.sales_segment_both_store_in,
            ticket_bundle=self.ticket_bundle_non_store
        )
        validate_ticket_bundle_and_sales_segment_set(
            field=self.dummy_field2,
            sales_segment=self.sales_segment_both_store_in,
            ticket_bundle=self.ticket_bundle_sej
        )
        validate_ticket_bundle_and_sales_segment_set(
            field=self.dummy_field3,
            sales_segment=self.sales_segment_both_store_in,
            ticket_bundle=self.ticket_bundle_fami
        )
        self.assertEqual(len(self.dummy_field1.errors), 1)
        self.assertEqual(len(self.dummy_field2.errors), 1)
        self.assertEqual(len(self.dummy_field3.errors), 1)

    def test_ticket_bundle_with_store_validation(self):
        """
        販売区分の引取方法にコンビニがあって、
        券面構成内にもコンビニがある場合は、
        validationに引っかからずメッセージも空になる
        """
        validate_ticket_bundle_and_sales_segment_set(
            field=self.dummy_field1,
            sales_segment=self.sales_segment_both_store_in,
            ticket_bundle=self.ticket_bundle_both
        )
        validate_ticket_bundle_and_sales_segment_set(
            field=self.dummy_field2,
            sales_segment=self.sales_segment_sej_in,
            ticket_bundle=self.ticket_bundle_sej
        )
        validate_ticket_bundle_and_sales_segment_set(
            field=self.dummy_field3,
            sales_segment=self.sales_segment_fami_in,
            ticket_bundle=self.ticket_bundle_fami
        )
        validate_ticket_bundle_and_sales_segment_set(
            field=self.dummy_field4,
            sales_segment=self.sales_segment_non_store_in,
            ticket_bundle=self.ticket_bundle_both
        )
        # コンビニ種類が合致する場合はエラー無し
        self.assertEqual(len(self.dummy_field1.errors), 0)
        self.assertEqual(len(self.dummy_field2.errors), 0)
        self.assertEqual(len(self.dummy_field3.errors), 0)
        # 券面に余分に紐付いていてもエラー無し
        self.assertEqual(len(self.dummy_field4.errors), 0)

if __name__ == "__main__":
    unittest.main()
