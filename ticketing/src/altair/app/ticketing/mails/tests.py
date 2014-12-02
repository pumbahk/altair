# -*- coding:utf-8 -*-

""" integreation test
"""

import unittest
from pyramid import testing
from altair.app.ticketing.testing import DummyRequest
from datetime import datetime

def create_initial_settings():
    from pyramid.path import AssetResolver
    sej_template_file = AssetResolver("altair.app.ticketing").resolve("../../misc/sej/template.html").abspath()
    return {"altair.mailer": "pyramid_mailer.testing", 
            'altair.sej.template_file': sej_template_file}    


class CompletMailSettingsTest(unittest.TestCase):
    def setUp(self):
        from altair.app.ticketing.testing import _setup_db
        from altair.sqlahelper import register_sessionmaker_with_engine
        self.session = _setup_db(modules=[
                "altair.app.ticketing.models",
                "altair.app.ticketing.orders.models",
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.cart.models",
                ])
        self.config = testing.setUp(settings={"altair.mailer": "pyramid_mailer.testing", "altair.sej.template_file": ""})
        self.config.include('pyramid_mako')
        self.config.include('altair.pyramid_dynamic_renderer')
        self.config.add_mako_renderer('.html')
        self.config.include('altair.app.ticketing.cart.import_mail_module')
        ## TBA
        self.config.add_route("qr.make", "__________")
        
        self.config.include('altair.app.ticketing.payments')
        self.config.include('altair.app.ticketing.payments.plugins')
        self.config.add_subscriber('altair.app.ticketing.cart.subscribers.add_helpers', 'pyramid.events.BeforeRender')
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )

    def tearDown(self):
        from altair.app.ticketing.testing import _teardown_db
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from altair.app.ticketing.mails import api
        return api

    def test_create_or_update_mailinfo_with_organization(self):
        from altair.app.ticketing.core.models import Organization
        organization = Organization()
        target = self._getTarget()
        request = None
        data = {u"footer": u"this-is-footer-message"}

        result = target.create_or_update_mailinfo(request, data, organization=organization)
        
        self.assertEquals(result.data["footer"],u"this-is-footer-message")
        self.assertEquals(result.organization, organization)

    def test_create_or_update_mailinfo_with_event(self):
        from altair.app.ticketing.core.models import Event
        event = Event()
        target = self._getTarget()
        request = None
        data = {u"footer": u"this-is-footer-message"}

        result = target.create_or_update_mailinfo(request, data, event=event)
        
        self.assertEquals(result.data["footer"],u"this-is-footer-message")
        self.assertEquals(result.event, event)

    def test_create_or_update_mailinfo_data_includeing_emptystring(self):
        from altair.app.ticketing.core.models import Organization
        organization = Organization()
        target = self._getTarget()
        request = None
        data = {u"footer": u"this-is-footer-message"}

        created = target.create_or_update_mailinfo(request, data, organization=organization)
        self.assertEquals(created.data["footer"],u"this-is-footer-message")

        updated = target.create_or_update_mailinfo(request, {u"footer": u""},  organization=organization)
        self.assertEquals(updated.data["footer"],u"")
        
    def test_create_or_update_mailinfo_with_event_using_organization_bound_one(self):
        from altair.app.ticketing.core.models import Organization
        from altair.app.ticketing.core.models import ExtraMailInfo
        from altair.app.ticketing.core.models import Event
        from altair.app.ticketing.mails.traverser import EmailInfoTraverser

        organization = Organization()
        organization.extra_mailinfo = ExtraMailInfo(data=dict(header="this-is-default-header"))

        event = Event(organization=organization)
        target = self._getTarget()
        request = None
        data = {u"footer": u"this-is-footer-message"}

        result = target.create_or_update_mailinfo(request, data, event=event)

        ## 新しく生成されたeventに結びつくMailInfoは直接親のOrganizationとは結びついていない。
        self.assertEquals(result.event, event)
        self.assertNotEquals(result.organization, organization)

        ## event, organizationに結びついたメールのデータが取得できる
        data_lookup = EmailInfoTraverser().visit(event)

        self.assertEquals(data_lookup.data["header"],u"this-is-default-header")
        self.assertEquals(data_lookup.data["footer"],u"this-is-footer-message")

class CreateMailFromFakeOrderTests(unittest.TestCase):
    def setUp(self):
        from altair.app.ticketing.testing import _setup_db
        from altair.sqlahelper import register_sessionmaker_with_engine
        self.session = _setup_db(modules=[
                "altair.app.ticketing.models",
                "altair.app.ticketing.orders.models",
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.cart.models",
                ])
        self.config = testing.setUp(settings={"altair.mailer": "pyramid_mailer.testing", "altair.sej.template_file": ""})
        self.config.include('pyramid_mako')
        self.config.include('altair.pyramid_dynamic_renderer')
        self.config.add_mako_renderer('.html')
        self.config.add_mako_renderer('.txt')
        self.config.include('altair.app.ticketing.mails.install_mail_utility')
        ## TBA
        self.config.add_route("qr.make", "__________")

        self.config.include('altair.app.ticketing.payments')
        self.config.include('altair.app.ticketing.payments.plugins')
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )
        from mock import patch
        self._patch_get_cart_setting_from_order_like = patch('altair.app.ticketing.cart.api.get_cart_setting_from_order_like')
        p = self._patch_get_cart_setting_from_order_like.start()
        p.return_value.type = 'standard'

    def tearDown(self):
        from altair.app.ticketing.testing import _teardown_db
        self._patch_get_cart_setting_from_order_like.stop()
        _teardown_db()
        testing.tearDown()

    def test_it(self):
        from altair.app.ticketing.core.models import Organization, MailTypeEnum, OrganizationSetting
        from altair.app.ticketing.mails.fake import FakeOrderFactory
        from altair.app.ticketing.mails.api import get_mail_utility

        org = Organization()
        org.settings.append(OrganizationSetting(name="default", contact_pc_url='pc@example.com', contact_mobile_url='mobile@exmaple.com'))
        org.extra_mail_info=None
        request = DummyRequest()
        order = FakeOrderFactory(object())(request, { "organization": org })

        mutil = get_mail_utility(request, MailTypeEnum.PurchaseCompleteMail)
        mutil.build_message(request, order).body
        mutil = get_mail_utility(request, MailTypeEnum.PurchaseCancelMail)
        mutil.build_message(request, order).body

    def test_lot_entry(self):
        from altair.app.ticketing.core.models import Organization, MailTypeEnum, OrganizationSetting, Performance, Event, Venue
        from altair.app.ticketing.mails.fake import FakeLotEntryElectedWishPairFactory
        from altair.app.ticketing.mails.api import get_mail_utility

        org = Organization()
        org.settings.append(OrganizationSetting(name="default"))
        org.extra_mail_info=None
        performance = Performance(event=Event(title=u"example"), start_on=datetime(2014, 1, 1, 0, 0, 0), end_on=datetime(2014, 1, 2, 23, 59, 59), venue=Venue(name=u'テスト会場'))
        request = DummyRequest()
        request.context = testing.DummyResource(organization=org)

        subject = FakeLotEntryElectedWishPairFactory(object())(request, { "organization": org, "performance": performance })

        mutil = get_mail_utility(request, MailTypeEnum.LotsAcceptedMail)
        mutil.build_message(request, subject).body
        mutil = get_mail_utility(request, MailTypeEnum.LotsElectedMail)
        mutil.build_message(request, subject).body
        mutil = get_mail_utility(request, MailTypeEnum.LotsRejectedMail)
        mutil.build_message(request, subject).body


class GetDefaultContactReferenceTest(unittest.TestCase):
    def _getTarget(self):
        from .api import get_default_contact_reference
        return get_default_contact_reference

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        from altair.app.ticketing.testing import _setup_db
        from altair.sqlahelper import register_sessionmaker_with_engine
        self.session = _setup_db(modules=[
                "altair.app.ticketing.models",
                "altair.app.ticketing.orders.models",
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.cart.models",
                ])
        self.request = DummyRequest()
        self.config = testing.setUp(request=self.request)
        self.config.include('altair.mobile')
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )

    def tearDown(self):
        from altair.app.ticketing.testing import _teardown_db
        _teardown_db()

    def test_http(self):
        organization = testing.DummyModel(
            setting=testing.DummyModel(
                contact_pc_url='http://example.com/pc',
                contact_mobile_url='http://example.com/mobile',
                default_mail_sender='sender@example.com'
                )
            )

        result = self._callFUT(self.request, organization, 'pc@example.com')
        self.assertEqual('http://example.com/pc', result)

        result = self._callFUT(self.request, organization, 'mobile@docomo.ne.jp')
        self.assertEqual('http://example.com/mobile', result)

    def test_mail(self):
        organization = testing.DummyModel(
            setting=testing.DummyModel(
                contact_pc_url='mailto:pc@example.com',
                contact_mobile_url='mailto:mobile@example.com',
                default_mail_sender='sender@example.com'
                )
            )

        result = self._callFUT(self.request, organization, 'pc@example.com')
        self.assertEqual('<pc@example.com>', result)

        result = self._callFUT(self.request, organization, 'mobile@docomo.ne.jp')
        self.assertEqual('<mobile@example.com>', result)

    def test_nothing(self):
        organization = testing.DummyModel(
            setting=testing.DummyModel(
                contact_pc_url=None,
                contact_mobile_url=None,
                default_mail_sender=None
                )
            )

        result = self._callFUT(self.request, organization, 'pc@example.com')
        self.assertEqual('', result)

        result = self._callFUT(self.request, organization, 'mobile@docomo.ne.jp')
        self.assertEqual('', result)

if __name__ == "__main__":
    unittest.main()
    
