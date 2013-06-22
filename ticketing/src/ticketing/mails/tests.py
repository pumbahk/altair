# -*- coding:utf-8 -*-

""" integreation test
"""

import unittest
from pyramid import testing
from datetime import datetime

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

def create_initial_settings():
    from pyramid.path import AssetResolver
    sej_template_file = AssetResolver("ticketing").resolve("../../misc/sej/template.html").abspath()
    return {"altair.mailer": "pyramid_mailer.testing", 
            'altair_sej.template_file': sej_template_file}    


class CompletMailSettingsTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={"altair.mailer": "pyramid_mailer.testing", "altair_sej.template_file": ""})
        self.config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
        self.config.include("ticketing.cart.import_mail_module")
        ## TBA
        self.config.add_route("qr.make", "__________")
        
        self.config.include("ticketing.payments")
        self.config.include("ticketing.payments.plugins")
        self.config.add_subscriber('ticketing.cart.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from ticketing.mails import api
        return api

    def test_create_or_update_mailinfo_with_organization(self):
        from ticketing.core.models import Organization
        organization = Organization()
        target = self._getTarget()
        request = None
        data = {u"footer": u"this-is-footer-message"}

        result = target.create_or_update_mailinfo(request, data, organization=organization)
        
        self.assertEquals(result.data["footer"],u"this-is-footer-message")
        self.assertEquals(result.organization, organization)

    def test_create_or_update_mailinfo_with_event(self):
        from ticketing.core.models import Event
        event = Event()
        target = self._getTarget()
        request = None
        data = {u"footer": u"this-is-footer-message"}

        result = target.create_or_update_mailinfo(request, data, event=event)
        
        self.assertEquals(result.data["footer"],u"this-is-footer-message")
        self.assertEquals(result.event, event)

    def test_create_or_update_mailinfo_data_includeing_emptystring(self):
        from ticketing.core.models import Organization
        organization = Organization()
        target = self._getTarget()
        request = None
        data = {u"footer": u"this-is-footer-message"}

        created = target.create_or_update_mailinfo(request, data, organization=organization)
        self.assertEquals(created.data["footer"],u"this-is-footer-message")

        updated = target.create_or_update_mailinfo(request, {u"footer": u""},  organization=organization)
        self.assertEquals(updated.data["footer"],u"")
        
    def test_create_or_update_mailinfo_with_event_using_organization_bound_one(self):
        from ticketing.core.models import Organization
        from ticketing.core.models import ExtraMailInfo
        from ticketing.core.models import Event
        from ticketing.mails.traverser import EmailInfoTraverser

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
        self.config = testing.setUp(settings={"altair.mailer": "pyramid_mailer.testing", "altair_sej.template_file": ""})
        self.config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
        self.config.add_renderer('.txt' , 'pyramid.mako_templating.renderer_factory')
        self.config.include("ticketing.mails.install_mail_utility")
        ## TBA
        self.config.add_route("qr.make", "__________")

        self.config.include("ticketing.payments")
        self.config.include("ticketing.payments.plugins")

    def tearDown(self):
        testing.tearDown()

    def test_it(self):
        from ticketing.core.models import Organization, MailTypeEnum
        from ticketing.mails.api import create_fake_order
        from ticketing.mails.api import get_mail_utility

        org = Organization()
        org.extra_mail_info=None
        request = testing.DummyRequest()
        order = create_fake_order(request, org, 2, 1)

        mutil = get_mail_utility(request, MailTypeEnum.PurchaseCompleteMail)
        mutil.build_message(request, order).body
        mutil = get_mail_utility(request, MailTypeEnum.PurchaseCancelMail)
        mutil.build_message(request, order).body

    def test_lot_entry(self):
        from ticketing.core.models import Organization, MailTypeEnum
        from ticketing.mails.api import create_fake_lot_entry
        from ticketing.mails.api import create_fake_elected_wish
        from ticketing.mails.api import get_mail_utility

        org = Organization()
        org.extra_mail_info=None
        request = testing.DummyRequest()
        request.context = testing.DummyResource(organization=org)

        lot_entry = create_fake_lot_entry(request, org, 2, 1)
        elected_wish = create_fake_elected_wish(request)
        subject = (lot_entry, elected_wish)

        mutil = get_mail_utility(request, MailTypeEnum.LotsAcceptedMail)
        mutil.build_message(request, subject).body
        mutil = get_mail_utility(request, MailTypeEnum.LotsElectedMail)
        mutil.build_message(request, subject).body
        mutil = get_mail_utility(request, MailTypeEnum.LotsRejectedMail)
        mutil.build_message(request, subject).body


if __name__ == "__main__":
    # setUpModule()
    unittest.main()
    
