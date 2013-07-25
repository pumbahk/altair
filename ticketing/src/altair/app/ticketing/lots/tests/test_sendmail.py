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
        import json
        from datetime import datetime
        import pyramid_mailer
        import altair.app.ticketing.core.models as core_models
        import altair.app.ticketing.lots.models as lots_models
        from altair.app.ticketing import txt_renderer_factory
        self.config.add_route('lots.review.index', 'review')
        self.config.add_renderer('.txt' , txt_renderer_factory)        
        self.config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')

        request = testing.DummyRequest()
        request.registry.settings['altair.mailer'] = 'pyramid_mailer.testing'
        self.config.include('altair.app.ticketing.lots.sendmail')

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
                                              contact_email="testing@sender.example.com", 
                                                          name=u"テスト組織",
                                                          settings=[
                                                              core_models.OrganizationSetting(name="default"),
                                                          ]),
                ),
                lotting_announce_datetime=datetime.now(),
                sales_segment=core_models.SalesSegment(),
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
        core_models.ExtraMailInfo(event=entry.lot.event, 
                                  data=json.dumps({unicode(core_models.MailTypeEnum.LotsAcceptedMail):
                                                       {"subject": u"抽選テスト 【テスト組織】", 
                                                        "sender": 'testing@sender.example.com', 
                                                        "event_name": {"use": True,  "kana": u"イベント名"}}}))

        result = self._callFUT(request, entry)

        mailer = pyramid_mailer.get_mailer(request)
        self.assertEqual(mailer.outbox, [result])
        self.assertEqual(result.subject, u"抽選テスト 【テスト組織】")
        self.assertEqual(result.sender, "testing@sender.example.com")
        self.assertEqual(result.recipients, ['testing@example.com'])
        self.assertIn(u'抽選テスト', result.body)

