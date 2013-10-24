#-*- coding: utf-8 -*-
"""The orderreview api tests.
"""
from unittest import TestCase
from mock import Mock


class GetContactURLTest(TestCase):
    """get_contact_url() test.
    """

    @staticmethod
    def _create_request():
        """Create Mock of request object.
        """
        # dummy data
        env = {'altair.app.ticketing.cart.organization_id': 1,
               'altair.app.ticketing.cart.organization_path': '/path/to/org',
               }

        request = Mock()
        request.organization = 'http://ticketstar.jp'
        request.environ = env
        return request

    @staticmethod
    def _create_setting():
        """Create mock of organization setting object.
        """
        pc_url = 'http://ticketstar.jp/pc'
        mobile_url = 'http://ticketstar.jp/mobile'
        setting = Mock()
        setting.contact_mobile_url = mobile_url
        setting.contact_pc_url = pc_url
        return setting

    def setUp(self):
        """Mock setup.
        """
        self.pc_url = 'http://ticketstar.jp/pc'
        self.mobile_url = 'http://ticketstar.jp/mobile'

        self.request = self._create_request()
        self.organization = Mock()
        self.organization.id = 1
        self.get_organization = Mock(return_value=self.organization)
        self.setting = self._create_setting()
        self.mobile_request = Mock(return_value=True)

        from .. import api
        api.get_organization = self.get_organization
        api.get_organization_setting = Mock(return_value=self.setting)
        api.is_mobile_request = self.mobile_request

    def normal_test(self):
        """Normal case.
        """
        from .. import api

        # mobile
        self.mobile_request.return_value = True
        url = api.get_contact_url(self.request)
        self.assertEqual(url, self.mobile_url)

        # pc
        self.mobile_request.return_value = False
        url = api.get_contact_url(self.request)
        self.assertEqual(url, self.pc_url)

    def invalid_url_test(self):
        """Invalid request case.
        """
        from .. import api
        error = ValueError

        # mobile
        self.mobile_request.return_value = True
        self.setting.contact_mobile_url = None
        with self.assertRaises(error):
            api.get_contact_url(self.request)

        with self.assertRaises(error):
            api.get_contact_url(self.request, error)

        # pc
        self.mobile_request.return_value = False
        self.setting.contact_pc_url = None
        with self.assertRaises(error):
            api.get_contact_url(self.request)

        with self.assertRaises(error):
            api.get_contact_url(self.request, error)

    def cannot_get_organization_test(self):
        """No organization case.
        """
        from .. import api
        self.get_organization.return_value = None

        error = ValueError
        with self.assertRaises(error):
            api.get_contact_url(self.request)

        with self.assertRaises(error):
            api.get_contact_url(self.request, error)
