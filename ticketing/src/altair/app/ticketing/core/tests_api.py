import unittest
from pyramid.testing import DummyModel, setUp, tearDown
from altair.app.ticketing.testing import DummyRequest
from altair.mobile.api import detect_from_email_address

class GetDefaultContactUrlTest(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _getTarget(self):
        from .api import get_default_contact_url
        return get_default_contact_url


    def setUp(self):
        request = DummyRequest()
        config = setUp(request=request)
        config.include('altair.mobile')
        self.request = request

    def tearDown(self):
        tearDown()

    def test_both_specified_pc(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url='http://example.com/contact/pc',
                contact_mobile_url='http://example.com/contact/mobile',
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@example.com')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'http://example.com/contact/pc')

    def test_both_specified_mobile(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url='http://example.com/contact/pc',
                contact_mobile_url='http://example.com/contact/mobile',
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@docomo.ne.jp')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'http://example.com/contact/mobile')

    def test_either_specified_pc_1(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url='http://example.com/contact/pc',
                contact_mobile_url=None,
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@example.com')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'http://example.com/contact/pc')

    def test_either_specified_pc_2(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url='http://example.com/contact/pc',
                contact_mobile_url=None,
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@docomo.ne.jp')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'mailto:default@example.com')

    def test_either_specified_mobile_1(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url=None,
                contact_mobile_url='http://example.com/contact/mobile',
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@example.com')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'mailto:default@example.com')

    def test_either_specified_mobile_2(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url=None,
                contact_mobile_url='http://example.com/contact/mobile',
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@docomo.ne.jp')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'http://example.com/contact/mobile')

    def test_none_specified_pc(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url=None,
                contact_mobile_url=None,
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@example.com')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'mailto:default@example.com')

    def test_none_specified_mobile(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url=None,
                contact_mobile_url=None,
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@docomo.ne.jp')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'mailto:default@example.com')
