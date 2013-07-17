# -*- coding:utf-8 -*-
import unittest
import mock
from pyramid import testing

from ..testing import DummyCheckout3D

class secure3d_enrolTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import secure3d_enrol
        return secure3d_enrol(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_it(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D()
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.app.ticketing.multicheckout.events.Secure3DEnrolEvent')
        request = testing.DummyRequest()
        order_no = 'test_order_no'
        card_number = 'x' * 16
        exp_year = '20'
        exp_month = '12'
        total_amount = 9999

        result = self._callFUT(
            request,
            order_no,
            card_number,
            exp_year,
            exp_month,
            total_amount)

        self.assertEqual(result.OrderNo, order_no)
        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'secure3d_enrol')

class secure3d_authTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import secure3d_auth
        return secure3d_auth(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_it(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D()
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.app.ticketing.multicheckout.events.Secure3DAuthEvent')
        request = testing.DummyRequest()
        order_no = 'test_order_no'
        pares = 'pares' * 30
        md = 'md' * 40

        result = self._callFUT(
            request,
            order_no,
            pares,
            md,)


        self.assertEqual(result.OrderNo, order_no)
        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'secure3d_auth')

class checkout_auth_secure3dTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import checkout_auth_secure3d
        return checkout_auth_secure3d(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_it(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D()
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.app.ticketing.multicheckout.events.CheckoutAuthSecure3DEvent')
        request = testing.DummyRequest()
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
        

        result = self._callFUT(
            request,
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
        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_auth_secure3d')

class checkout_salesTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import checkout_sales
        return checkout_sales(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_it(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D()
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.app.ticketing.multicheckout.events.CheckoutSalesSecure3DEvent')
        request = testing.DummyRequest()
        order_no = 'test_order_no'        

        result = self._callFUT(
            request,
            order_no,
            )


        self.assertEqual(result.OrderNo, order_no)
        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_sales_secure3d')

class checkout_auth_cancelTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import checkout_auth_cancel
        return checkout_auth_cancel(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_it(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D()
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.app.ticketing.multicheckout.events.CheckoutAuthCancelEvent')
        request = testing.DummyRequest()
        order_no = 'test_order_no'        

        result = self._callFUT(
            request,
            order_no,
            )


        self.assertEqual(result.OrderNo, order_no)
        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_auth_cancel')


class checkout_sales_part_cancelTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import checkout_sales_part_cancel
        return checkout_sales_part_cancel(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_it(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D()
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.app.ticketing.multicheckout.events.CheckoutSalesPartCancelEvent')
        request = testing.DummyRequest()
        order_no = 'test_order_no'        
        sales_amount_cancellation = 999
        tax_carriage_cancellation = 9
        result = self._callFUT(
            request,
            order_no,
            sales_amount_cancellation,
            tax_carriage_cancellation,
            )


        self.assertEqual(result.OrderNo, order_no)
        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_sales_part_cancel')


class checkout_sales_cancelTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import checkout_sales_cancel
        return checkout_sales_cancel(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_it(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D()
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.app.ticketing.multicheckout.events.CheckoutSalesCancelEvent')
        request = testing.DummyRequest()
        order_no = 'test_order_no'        
        result = self._callFUT(
            request,
            order_no,
            )


        self.assertEqual(result.OrderNo, order_no)
        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_sales_cancel')


class checkout_inquiryTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import checkout_inquiry
        return checkout_inquiry(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_it(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D()
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.app.ticketing.multicheckout.events.CheckoutInquiryEvent')
        request = testing.DummyRequest()
        order_no = 'test_order_no'        
        result = self._callFUT(
            request,
            order_no,
            )


        self.assertEqual(result.OrderNo, order_no)
        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_inquiry')


class checkout_auth_secure_codeTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import checkout_auth_secure_code
        return checkout_auth_secure_code(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_it(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D()
        mock_handler = mock.Mock()
        self.config.add_subscriber(mock_handler,
                                   'altair.app.ticketing.multicheckout.events.CheckoutAuthSecureCodeEvent')
        request = testing.DummyRequest()
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
        

        result = self._callFUT(
            request,
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
        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler.call_args[0][0].api, 'checkout_auth_secure_code')


class checkout_sales_different_amountTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import checkout_sales_different_amount
        return checkout_sales_different_amount(*args, **kwargs)

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_it(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D()
        mock_handler1 = mock.Mock()
        self.config.add_subscriber(mock_handler1,
                                   'altair.app.ticketing.multicheckout.events.CheckoutSalesSecure3DEvent')
        mock_handler2 = mock.Mock()
        self.config.add_subscriber(mock_handler2,
                                   'altair.app.ticketing.multicheckout.events.CheckoutSalesPartCancelEvent')
        request = testing.DummyRequest()
        order_no = 'test_order_no'
        different_amount = 999

        result = self._callFUT(
            request,
            order_no,
            different_amount,
            )

        print mock_handler1.call_args
        print mock_handler2.call_args

        self.assertEqual(result.OrderNo, order_no)

        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler1.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler1.call_args[0][0].api, 'checkout_sales_secure3d')

        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler2.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler2.call_args[0][0].api, 'checkout_sales_part_cancel')

    @mock.patch('altair.app.ticketing.multicheckout.api.save_api_response')
    @mock.patch('altair.app.ticketing.multicheckout.api.get_multicheckout_service')
    def test_with_sales_error(self, mock_service_factory, mock_save_api_response):
        mock_service_factory.return_value = DummyCheckout3D(CmnErrorCd='999999')
        mock_handler1 = mock.Mock()
        self.config.add_subscriber(mock_handler1,
                                   'altair.app.ticketing.multicheckout.events.CheckoutSalesSecure3DEvent')
        mock_handler2 = mock.Mock()
        self.config.add_subscriber(mock_handler2,
                                   'altair.app.ticketing.multicheckout.events.CheckoutSalesPartCancelEvent')
        request = testing.DummyRequest()
        order_no = 'test_order_no'
        different_amount = 999

        result = self._callFUT(
            request,
            order_no,
            different_amount,
            )


        self.assertEqual(result.OrderNo, order_no)
        self.assertEqual(result.CmnErrorCd, '999999')

        mock_save_api_response.assert_called_with(request, result)
        self.assertEqual(mock_handler1.call_args[0][0].order_no, 'test_order_no')
        self.assertEqual(mock_handler1.call_args[0][0].api, 'checkout_sales_secure3d')

        mock_save_api_response.assert_not_called()
