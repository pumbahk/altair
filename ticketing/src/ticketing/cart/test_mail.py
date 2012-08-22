# -*- coding:utf-8 -*-

""" TBA
"""

import unittest
from pyramid import testing

def setUpModule():
    from ticketing.testing import _setup_db
    _setup_db(modules=[
            "ticketing.models",
            "ticketing.core.models",
            "ticketing.cart.models",
            ])

def tearDownModule():
    from ticketing.testing import _teardown_db
    _teardown_db()

class MailCreateUnitTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={"altair.mailer": "ticketing.cart.sendmail.devnull_mailer"})
        self.config.include("ticketing.cart.import_mail_module")

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ticketing.cart.events import notify_order_completed
        notify_order_completed(*args, **kwargs)
        
    def test_notify_success(self):
        from pyramid.interfaces import IRequest
        from ticketing.cart.interfaces import ICompleteMail

        class DummyCompleteMail(object):
            def __init__(self, request):
                self.request = request

            def build_message(self, order):
                self.__class__._called = "build_message"
                self.__class__._order = order
                return testing.DummyResource(recipients="")
               
        self.config.registry.adapters.register([IRequest], ICompleteMail, "", DummyCompleteMail)
        request = testing.DummyRequest()
        order = object()
        self._callFUT(request, order)

        self.assertEquals(DummyCompleteMail._called, "build_message")
        self.assertEquals(DummyCompleteMail._order, order)
        
    def test_exception_in_send_mail_action(self):
        pass

    def test_payment_by_card_delivery_by_qr(self):
        pass
        # from altaircms.
        # request = testing.DummyRequest()
        # order = 

    def test_payment_by_card_delivery_by_seven(self):
        pass

    def test_payment_by_card_delivery_home(self):
        pass

    def test_payment_by_seven_delivery_by_seven(self):
        pass

    def test_payment_unknown_delivery_by_unknown(self):
        pass

if __name__ == "__main__":
    # setUpModule()
    unittest.main()
    
