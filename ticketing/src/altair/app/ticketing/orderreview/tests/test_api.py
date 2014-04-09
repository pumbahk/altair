#-*- coding: utf-8 -*-
"""The orderreview api tests.
"""
from unittest import TestCase
from mock import Mock, patch

from .. import api


class _TestException(Exception):
    """Dummy exception.
    """
    pass


class GetContactURLTest(TestCase):
    """get_contact_url() test.
    """
    pc_url = 'http://ticketstar.jp/pc'
    mobile_url = 'http://ticketstar.jp/mobile'

    @staticmethod
    def _create_request(organization):
        """Create Mock of request object.
        """
        # dummy data
        env = {'altair.app.ticketing.cart.organization_id': 1,
               'altair.app.ticketing.cart.organization_path': '/path/to/org',
               }
        request = Mock()
        request.organization = organization
        request.environ = env
        return request

    @staticmethod
    def _create_organization():
        """Create mock of organization object.
        """
        organization = Mock()
        organization.id = 1
        return organization

    @classmethod
    def _create_setting(cls):
        """Create mock of organization setting object.
        """
        setting = Mock()
        setting.contact_mobile_url = cls.mobile_url
        setting.contact_pc_url = cls.pc_url
        return setting

    @classmethod
    def _setup_normal_mock(cls, get_organization, get_organization_setting):
        """Set up normal data to mock objects.
        """
        get_organization.return_value \
            = organization = cls._create_organization()
        organization.setting = get_organization_setting.return_value = setting = cls._create_setting()
        request = cls._create_request(organization)
        return request, organization, setting

    @patch('altair.app.ticketing.orderreview.api.get_organization_setting')
    @patch('altair.app.ticketing.orderreview.api.get_organization')
    def normal_test(self, get_organization, get_organization_setting):
        """Normal case.
        """
        request, organization, setting \
            = self._setup_normal_mock(get_organization, get_organization_setting)

        from altair.mobile.carriers import NonMobile, DoCoMo
        # mobile
        request.mobile_ua.carrier = DoCoMo
        url = api.get_contact_url(request)
        self.assertEqual(url, self.mobile_url)

        # pc
        request.mobile_ua.carrier = NonMobile
        url = api.get_contact_url(request)
        self.assertEqual(url, self.pc_url)

    @patch('altair.app.ticketing.orderreview.api.get_organization_setting')
    @patch('altair.app.ticketing.orderreview.api.get_organization')
    def invalid_url_test(self, get_organization, get_organization_setting):

        """Invalid request case.
        """
        request, organization, setting \
            = self._setup_normal_mock(get_organization, get_organization_setting)
        error = _TestException

        from altair.mobile.carriers import NonMobile, DoCoMo
        # mobile
        request.mobile_ua.carrier = DoCoMo
        setting.default_mail_sender = None
        setting.contact_mobile_url = None
        with self.assertRaises(ValueError):
            api.get_contact_url(request)

        with self.assertRaises(error):
            api.get_contact_url(request, error)

        # pc
        request.mobile_ua.carrier = DoCoMo
        setting.contact_pc_url = None
        with self.assertRaises(ValueError):
            api.get_contact_url(request)

        with self.assertRaises(error):
            api.get_contact_url(request, error)

    @patch('altair.app.ticketing.orderreview.api.get_organization_setting')
    @patch('altair.app.ticketing.orderreview.api.get_organization')
    def cannot_get_organization_test(self, get_organization, get_organization_setting):
        """No organization case.
        """
        request, organization, setting \
            = self._setup_normal_mock(get_organization, get_organization_setting)

        from altair.mobile.carriers import NonMobile
        request.mobile_ua.carrier = NonMobile
        get_organization.return_value = None

        with self.assertRaises(ValueError):
            api.get_contact_url(request)

        error = _TestException
        with self.assertRaises(error):
            api.get_contact_url(request, error)
