# -*- coding:utf-8 -*-

import unittest
from pyramid import testing

class send_accepted_mailTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..sendmail import send_accepted_mail
        return send_accepted_mail(*args, **kwargs)


    def test_it(self):
        import pyramid_mailer
        import ticketing.core.models as core_models
        import ticketing.lots.models as lots_models
        self.config.add_route('lots.review.index', 'review')
        self.config.add_renderer('.txt' , 'pyramid.mako_templating.renderer_factory')

        self.config.include('pyramid_mailer.testing')
        request = testing.DummyRequest()
        request.registry.settings['lots.accepted_mail_subject'] = '抽選テスト'
        request.registry.settings['lots.accepted_mail_sender'] = 'testing@sender.example.com'
        request.registry.settings['lots.accepted_mail_template'] = 'ticketing.lots:mail_templates/accept_entry.txt'

        entry = lots_models.LotEntry(
            entry_no='TEST-LOT-ENTRY-NO',
            shipping_address=core_models.ShippingAddress(
                email=u"testing@example.com",
                first_name=u"",
                last_name=u"",
                first_name_kana=u"",
                last_name_kana=u"",
            ),
            lot=lots_models.Lot(
                name=u"抽選テスト",
                event=core_models.Event(
                    title=u"抽選テストイベント",
                ),
            ),
            payment_delivery_method_pair=core_models.PaymentDeliveryMethodPair(
                payment_method=core_models.PaymentMethod(
                ),
                delivery_method=core_models.DeliveryMethod(
                ),
            ),
        )

        result = self._callFUT(request, entry)

        mailer = pyramid_mailer.get_mailer(request)
        self.assertEqual(mailer.outbox, [result])
        self.assertEqual(result.subject, u"抽選テスト")
        self.assertEqual(result.sender, "testing@sender.example.com")
        self.assertEqual(result.recipients, ['testing@example.com'])
        self.assertIn(u'抽選テスト', result.body)
