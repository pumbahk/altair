# -*- coding:utf-8 -*-
import unittest
import mock
from pyramid import testing

class Multicheckout3DAPITests(unittest.TestCase):
    def setUp(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session
        from ..testing import DummyCheckout3D
        import sqlahelper

        self.config = testing.setUp()
        self.dummy_impl = DummyCheckout3D()
        self.request = testing.DummyRequest()
        engine = create_engine("sqlite:///")
        sqlahelper.add_engine(engine)
        self.session = Session(bind=engine)

        from .. import models

        sqlahelper.get_base().metadata.create_all()

    def tearDown(self):
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()
        testing.tearDown()

    def _getTarget(self):
        from ..api import Multicheckout3DAPI
        return Multicheckout3DAPI

    def _makeOne(self, **kwargs):
        return self._getTarget()(self.request, self.dummy_impl, self.session, **kwargs)

    def test_secure3d_enrol(self):
        from .. import models as m
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.multicheckout.events.Secure3DEnrolEvent')
        order_no = 'test_order_no'
        card_number = 'x' * 16
        exp_year = '20'
        exp_month = '12'
        total_amount = 9999

        target = self._makeOne()
        result = target.secure3d_enrol(
            order_no,
            card_number,
            exp_year,
            exp_month,
            total_amount)

        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'secure3d_enrol')
        self.assertEqual(self.session.query(m.Secure3DReqEnrolResponse).all(), [result])

    def test_secure3d_auth(self):
        from .. import models as m
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.multicheckout.events.Secure3DAuthEvent')

        order_no = 'test_order_no'
        pares = 'pares' * 30
        md = 'md' * 40

        target = self._makeOne()
        result = target.secure3d_auth(
            order_no,
            pares,
            md,)

        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'secure3d_auth')
        self.assertEqual(self.session.query(m.Secure3DAuthResponse).all(), [result])

    def test_checkout_auth_secure3d(self):
        from .. import models as m
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.multicheckout.events.CheckoutAuthSecure3DEvent')
        order_no = 'test_order_no'
        item_name = 'testing item'
        amount = "1000"
        tax = "0"
        client_name = "あああああ"
        mail_address = "testing@example.com"
        card_no = "x" * 16
        card_limit = "13/09"
        card_holder_name = "TEST CARD"
        mvn = "mvn" * 40
        xid = "xid" * 50
        ts = "ts" * 30
        eci = "eci" * 20
        cavv = "cavv"
        cavv_algorithm = "cavv_al"

        target = self._makeOne()
        result = target.checkout_auth_secure3d(
            order_no,
            item_name,
            amount,
            tax,
            client_name,
            mail_address,
            card_no,
            card_limit,
            card_holder_name,
            mvn,
            xid,
            ts,
            eci,
            cavv,
            cavv_algorithm,
            )

        self.assertEqual(result.OrderNo, order_no)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_auth_secure3d')
        self.assertEqual(self.session.query(m.MultiCheckoutResponseCard).all(), [result])

    def test_checkout_sales(self):
        from .. import models as m
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.multicheckout.events.CheckoutSalesSecure3DEvent')
        order_no = 'test_order_no'        

        target = self._makeOne()
        result = target.checkout_sales(order_no)

        self.assertEqual(result.OrderNo, order_no)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_sales_secure3d')
        self.assertEqual(self.session.query(m.MultiCheckoutResponseCard).all(), [result])

    def test_checkout_auth_cancel(self):
        from .. import models as m
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.multicheckout.events.CheckoutAuthCancelEvent')
        order_no = 'test_order_no'        

        target = self._makeOne()
        result = target.checkout_auth_cancel(
            order_no,
            )

        self.assertEqual(result.OrderNo, order_no)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_auth_cancel')
        self.assertEqual(self.session.query(m.MultiCheckoutResponseCard).all(), [result])

    def test_checkout_part_cancel(self):
        from .. import models as m
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.multicheckout.events.CheckoutSalesPartCancelEvent')
        order_no = 'test_order_no'        
        sales_amount_cancellation = 999
        tax_carriage_cancellation = 9
        target = self._makeOne()
        result = target.checkout_sales_part_cancel(
            order_no,
            sales_amount_cancellation,
            tax_carriage_cancellation,
            )


        self.assertEqual(result.OrderNo, order_no)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_sales_part_cancel')
        self.assertEqual(self.session.query(m.MultiCheckoutResponseCard).all(), [result])


    def test_checkout_sales_cancel(self):
        from .. import models as m
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.multicheckout.events.CheckoutSalesCancelEvent')
        order_no = 'test_order_no'        
        target = self._makeOne()
        result = target.checkout_sales_cancel(order_no)
        self.assertEqual(result.OrderNo, order_no)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_sales_cancel')
        self.assertEqual(self.session.query(m.MultiCheckoutResponseCard).all(), [result])

    def test_checkout_inquiry_cancel(self):
        from .. import models as m
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.multicheckout.events.CheckoutInquiryEvent')
        order_no = 'test_order_no'
        target = self._makeOne()
        result = target.checkout_inquiry(order_no)

        self.assertEqual(result.OrderNo, order_no)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_inquiry')
        self.assertEqual(self.session.query(m.MultiCheckoutInquiryResponseCard).all(), [result])

    def test_checkout_auth_secure_code(self):
        from .. import models as m
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.multicheckout.events.CheckoutAuthSecureCodeEvent')
        order_no = 'test_order_no'
        item_name = 'testing item'
        amount = "1000"
        tax = "0"
        client_name = "あああああ"
        mail_address = "testing@example.com"
        card_no = "x" * 16
        card_limit = "13/09"
        card_holder_name = "TEST CARD"
        secure_code = 'SECURE'
        

        target = self._makeOne()
        result = target.checkout_auth_secure_code(
            order_no,
            item_name,
            amount,
            tax,
            client_name,
            mail_address,
            card_no,
            card_limit,
            card_holder_name,
            secure_code,
            )


        self.assertEqual(result.OrderNo, order_no)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_auth_secure_code')
        self.assertEqual(self.session.query(m.MultiCheckoutResponseCard).all(), [result])


    def test_checkout_sales_different_amount(self):
        from .. import models as m
        mock_handler1 = mock.Mock()
        self.config.add_subscriber(mock_handler1,
                                   'altair.multicheckout.events.CheckoutSalesSecure3DEvent')
        mock_handler2 = mock.Mock()
        self.config.add_subscriber(mock_handler2,
                                   'altair.multicheckout.events.CheckoutSalesPartCancelEvent')
        order_no = 'test_order_no'
        different_amount = 999

        target = self._makeOne()
        result = target.checkout_sales_different_amount(
            order_no,
            different_amount,
            )

        print mock_handler1.call_args
        print mock_handler2.call_args

        self.assertEqual(result.OrderNo, order_no)
        self.assertEqual(mock_handler1.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler1.call_args[0][0].api, 'checkout_sales_secure3d')

        self.assertEqual(mock_handler2.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler2.call_args[0][0].api, 'checkout_sales_part_cancel')
        results = self.session.query(m.MultiCheckoutResponseCard).all()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[1], result)

    def test_with_sales_error(self):
        from ..testing import DummyCheckout3D
        from .. import models as m
        self.dummy_impl = DummyCheckout3D(CmnErrorCd='999999')
        mock_handler1 = mock.Mock()
        self.config.add_subscriber(mock_handler1,
                                   'altair.multicheckout.events.CheckoutSalesSecure3DEvent')
        mock_handler2 = mock.Mock()
        self.config.add_subscriber(mock_handler2,
                                   'altair.multicheckout.events.CheckoutSalesPartCancelEvent')
        request = testing.DummyRequest()
        order_no = 'test_order_no'
        different_amount = 999

        target = self._makeOne()
        result = target.checkout_sales_different_amount(
            order_no,
            different_amount,
            )


        self.assertEqual(result.OrderNo, order_no)
        self.assertEqual(result.CmnErrorCd, '999999')
        self.assertEqual(mock_handler1.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler1.call_args[0][0].api, 'checkout_sales_secure3d')
        self.assertEqual(self.session.query(m.MultiCheckoutResponseCard).all(), [result])
