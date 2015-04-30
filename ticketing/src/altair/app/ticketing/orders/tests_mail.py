# -*- coding:utf-8 -*-

import unittest
from datetime import datetime
from pyramid.testing import DummyModel, DummyRequest, setUp, tearDown
from altair.app.ticketing.mails.testing import MailTestMixin


class send_refund_reserve_mailTests(unittest.TestCase, MailTestMixin):

    def setUp(self):
        self.config = setUp()
        self.config.include('altair.pyramid_dynamic_renderer')
        self.config.include('pyramid_mako')
        self.config.add_mako_renderer('.txt')
        self.config.include('altair.app.ticketing.mails')
        self.config.include('altair.app.ticketing.renderers')
        self.registerDummyMailer()

    def tearDown(self):
        tearDown()

    def _callFUT(self, *args, **kwargs):
        from .mail import send_refund_reserve_mail
        return send_refund_reserve_mail(*args, **kwargs)

    def test_it(self):
        import pyramid_mailer
        import altair.app.ticketing.core.models as core_models

        request = DummyRequest()
        request.registry.settings['altair.mailer'] = 'pyramid_mailer.testing'
        request.registry.settings['mail.message.sender'] = 'sender@example.com'
        request.registry.settings['mail.report.recipient'] = 'report@example.com'
        refund = DummyModel(
            created_at=datetime(2014, 1, 1, 23),
            order_count=10,
            include_item=1,
            include_system_fee=1,
            include_transaction_fee=1,
            include_delivery_fee=1,
            include_special_fee=1,
            need_stub=1,
            start_at=datetime(2014, 1, 2),
            end_at=datetime(2014, 1, 9),
            performances=[DummyModel(name=u'公演1')],
            payment_method=DummyModel(name=u'コンビニ決済'),
            organization=DummyModel(contact_email=u'testing@example.com'),
        )

        mail_refund_to_user = False
        orders = None
        result = self._callFUT(request, refund, mail_refund_to_user, orders)

        mailer = pyramid_mailer.get_mailer(request)
        self.assertTrue(result)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject, u'[払戻予約] 公演1')
        self.assertEqual(mailer.outbox[0].sender, u'sender@example.com')
        self.assertEqual(mailer.outbox[0].recipients, [u'testing@example.com', u'report@example.com'])


class send_refund_complete_mailTests(unittest.TestCase, MailTestMixin):

    def setUp(self):
        self.config = setUp()
        self.config.include('altair.pyramid_dynamic_renderer')
        self.config.include('pyramid_mako')
        self.config.add_mako_renderer('.txt')
        self.config.include('altair.app.ticketing.mails')
        self.config.include('altair.app.ticketing.renderers')
        self.registerDummyMailer()

    def tearDown(self):
        tearDown()

    def _callFUT(self, *args, **kwargs):
        from .mail import send_refund_complete_mail
        return send_refund_complete_mail(*args, **kwargs)

    def test_it(self):
        import pyramid_mailer
        import altair.app.ticketing.core.models as core_models

        request = DummyRequest()
        request.registry.settings['altair.mailer'] = 'pyramid_mailer.testing'
        request.registry.settings['mail.message.sender'] = 'sender@example.com'
        request.registry.settings['mail.report.recipient'] = 'report@example.com'
        refund = DummyModel(
            updated_at=datetime(2014, 1, 1, 23),
            order_count=10,
            include_item=1,
            include_system_fee=1,
            include_transaction_fee=1,
            include_delivery_fee=1,
            include_special_fee=1,
            need_stub=1,
            start_at=datetime(2014, 1, 2),
            end_at=datetime(2014, 1, 9),
            performances=[DummyModel(name=u'公演1'), DummyModel(name=u'公演2')],
            payment_method=DummyModel(name=u'コンビニ決済'),
            organization=DummyModel(contact_email=u'testing@example.com'),
        )

        result = self._callFUT(request, refund)

        mailer = pyramid_mailer.get_mailer(request)
        self.assertTrue(result)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject, u'[払戻完了] 公演1, 公演2')
        self.assertEqual(mailer.outbox[0].sender, u'sender@example.com')
        self.assertEqual(mailer.outbox[0].recipients, [u'testing@example.com', u'report@example.com'])


class send_refund_error_mailTests(unittest.TestCase, MailTestMixin):

    def setUp(self):
        self.config = setUp()
        self.config.include('altair.pyramid_dynamic_renderer')
        self.config.include('pyramid_mako')
        self.config.add_mako_renderer('.txt')
        self.config.include('altair.app.ticketing.mails')
        self.config.include('altair.app.ticketing.renderers')
        self.registerDummyMailer()

    def tearDown(self):
        tearDown()

    def _callFUT(self, *args, **kwargs):
        from .mail import send_refund_error_mail
        return send_refund_error_mail(*args, **kwargs)

    def test_it(self):
        import pyramid_mailer
        import altair.app.ticketing.core.models as core_models

        request = DummyRequest()
        request.registry.settings['altair.mailer'] = 'pyramid_mailer.testing'
        request.registry.settings['mail.message.sender'] = 'sender@example.com'
        request.registry.settings['mail.report.recipient'] = 'report@example.com'
        refund = DummyModel(
            created_at=datetime(2014, 1, 1, 23),
            order_count=10,
            include_item=1,
            include_system_fee=1,
            include_transaction_fee=1,
            include_delivery_fee=1,
            include_special_fee=1,
            need_stub=1,
            start_at=datetime(2014, 1, 2),
            end_at=datetime(2014, 1, 9),
            performances=[DummyModel(name=u'公演1'), DummyModel(name=u'公演2')],
            payment_method=DummyModel(name=u'コンビニ決済'),
            organization=DummyModel(contact_email=u'testing@example.com'),
        )
        message = [u'エラー1', u'エラー2']

        result = self._callFUT(request, refund, message)

        mailer = pyramid_mailer.get_mailer(request)
        self.assertTrue(result)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(mailer.outbox[0].subject, u'[払戻エラー] 公演1, 公演2')
        self.assertEqual(mailer.outbox[0].sender, u'sender@example.com')
        self.assertEqual(mailer.outbox[0].recipients, [u'testing@example.com', u'report@example.com'])
