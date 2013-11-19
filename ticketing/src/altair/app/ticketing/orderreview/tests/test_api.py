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
    def _setup_normal_mock(cls, get_organization,
                           get_organization_setting, is_mobile_request):
        """Set up normal data to mock objects.
        """
        get_organization.return_value \
            = organization = cls._create_organization()
        get_organization_setting.return_value = setting = cls._create_setting()
        is_mobile_request.return_value = True
        request = cls._create_request(organization)
        return request, organization, setting

    @patch('altair.app.ticketing.orderreview.api.is_mobile_request')
    @patch('altair.app.ticketing.orderreview.api.get_organization_setting')
    @patch('altair.app.ticketing.orderreview.api.get_organization')
    def normal_test(self, get_organization,
                    get_organization_setting, is_mobile_request):
        """Normal case.
        """
        request, organization, setting \
            = self._setup_normal_mock(get_organization,
                                      get_organization_setting,
                                      is_mobile_request,
                                      )

        # mobile
        is_mobile_request.return_value = True
        url = api.get_contact_url(request)
        self.assertEqual(url, self.mobile_url)

        # pc
        is_mobile_request.return_value = False
        url = api.get_contact_url(request)
        self.assertEqual(url, self.pc_url)

    @patch('altair.app.ticketing.orderreview.api.is_mobile_request')
    @patch('altair.app.ticketing.orderreview.api.get_organization_setting')
    @patch('altair.app.ticketing.orderreview.api.get_organization')
    def invalid_url_test(self, get_organization,
                         get_organization_setting, is_mobile_request):

        """Invalid request case.
        """
        request, organization, setting \
            = self._setup_normal_mock(get_organization,
                                      get_organization_setting,
                                      is_mobile_request,
                                      )
        error = _TestException

        # mobile
        is_mobile_request.return_value = True
        setting.contact_mobile_url = None
        with self.assertRaises(ValueError):
            api.get_contact_url(request)

        with self.assertRaises(error):
            api.get_contact_url(request, error)

        # pc
        is_mobile_request.return_value = False
        setting.contact_pc_url = None
        with self.assertRaises(ValueError):
            api.get_contact_url(request)

        with self.assertRaises(error):
            api.get_contact_url(request, error)

    @patch('altair.app.ticketing.orderreview.api.is_mobile_request')
    @patch('altair.app.ticketing.orderreview.api.get_organization_setting')
    @patch('altair.app.ticketing.orderreview.api.get_organization')
    def cannot_get_organization_test(self, get_organization,
                                     get_organization_setting,
                                     is_mobile_request):
        """No organization case.
        """
        request, organization, setting \
            = self._setup_normal_mock(get_organization,
                                      get_organization_setting,
                                      is_mobile_request,
                                      )

        get_organization.return_value = None

        with self.assertRaises(ValueError):
            api.get_contact_url(request)

        error = _TestException
        with self.assertRaises(error):
            api.get_contact_url(request, error)
