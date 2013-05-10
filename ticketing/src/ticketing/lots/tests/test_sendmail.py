# -*- coding:utf-8 -*-

import unittest
from pyramid import testing


class get_mail_infoTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..sendmail import get_mail_info
        return get_mail_info(*args, **kwargs)


    def test_it(self):
        from ticketing.core.models import Event, ExtraMailInfo, Organization
        from ticketing.lots.models import Lot
        from ticketing.mails.traverser import EmailInfoTraverser
        self.config.registry.registerUtility(EmailInfoTraverser(default={}), name="lots")
        lot = Lot(
            event=Event(
                extra_mailinfo=ExtraMailInfo(
                    data={'subject': 'testing_event'}),
                organization=Organization(
                    extra_mailinfo=ExtraMailInfo(
                        data={'subject': 'testing_organization'}),
                    )))
        request = testing.DummyRequest()
        result = self._callFUT(request, lot)

        self.assertEqual(result.d, {'subject': 'testing_event'})


class MailSenderTests(unittest.TestCase):
    def _getTarget(self):
        from ..sendmail import MailSender
        return MailSender

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        subject = u"テスト"
        sender = u"testing@example.com"
        tmpl_name = 'ticketing.lots:test_mail.txt'

        target = self._makeOne(subject=subject,
                               sender=sender,
                               tmpl_name=tmpl_name)

        self.assertEqual(target.subject, subject)
        self.assertEqual(target.sender, sender)
        self.assertEqual(target.tmpl_name, tmpl_name)

    def test_send(self):
        pass


class send_accepted_mailTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..sendmail import send_accepted_mail
        return send_accepted_mail(*args, **kwargs)


    def test_it(self):
        from datetime import datetime
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
        self.config.include('ticketing.lots.sendmail')

        entry = lots_models.LotEntry(
            created_at=datetime.now(),
            entry_no='TEST-LOT-ENTRY-NO',
            shipping_address=core_models.ShippingAddress(
                email_1=u"testing@example.com",
                first_name=u"",
                last_name=u"",
                first_name_kana=u"",
                last_name_kana=u"",
            ),
            lot=lots_models.Lot(
                name=u"抽選テスト",
                event=core_models.Event(
                    title=u"抽選テストイベント",
                    organization=core_models.Organization(short_name='testing', 
                                              name=u"テスト組織"),
                ),
                lotting_announce_datetime=datetime.now(),
            ),
            payment_delivery_method_pair=core_models.PaymentDeliveryMethodPair(
                system_fee=0,
                payment_method=core_models.PaymentMethod(
                    fee_type=0,
                ),
                delivery_method=core_models.DeliveryMethod(
                    fee_type=1,
                ),
                transaction_fee=0,
                delivery_fee=115,
            ),
            wishes=[lots_models.LotEntryWish(wish_order=1,
                                             performance=core_models.Performance(
                                                 start_on=datetime.now(),
                                                 open_on=datetime.now(),
                                                 venue=core_models.Venue()),
                                             products=[])],
        )

        result = self._callFUT(request, entry)

        mailer = pyramid_mailer.get_mailer(request)
        self.assertEqual(mailer.outbox, [result])
        self.assertEqual(result.subject, u"抽選テスト 【テスト組織】")
        self.assertEqual(result.sender, "testing@sender.example.com")
        self.assertEqual(result.recipients, ['testing@example.com'])
        self.assertIn(u'抽選テスト', result.body)

