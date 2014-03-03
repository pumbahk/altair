import unittest
import mock
from pyramid.testing import setUp, tearDown, DummyRequest
from altair.app.ticketing.testing import _setup_db, _teardown_db

class MulticheckoutSettingTest(unittest.TestCase):
    def setUp(self):
        from altair.app.ticketing.core.models import Organization, OrganizationSetting, Host
        self.config = setUp(settings={
            'altair.multicheckout.endpoint.base_url': 'example.com',
            'altair.multicheckout.endpoint.timeout': 10,
            })
        self.config.include('altair.app.ticketing.multicheckout')
        self.config.include('altair.multicheckout')
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.multicheckout.models',
            ])
        organization_settings = []
        for i in range(0, 3):
            organization = Organization(
                short_name=u'%02d' % i
                )
            organization_setting = OrganizationSetting(
                multicheckout_shop_name=u'shop-name-%d' % i,
                multicheckout_shop_id=u'%d' % i,
                multicheckout_auth_id=u'api-id-%d' % i,
                multicheckout_auth_password=u'auth-password-%d' % i,
                organization=organization
                )
            host = Host(
                host_name='x%d.example.com' % i,
                organization=organization
                )
            self.session.add(organization)
            self.session.add(organization_setting)
            self.session.add(host)
            organization_settings.append(organization_setting)
        self.organization_settings = organization_settings
        self.session.flush()

    def tearDown(self):
        _teardown_db()
        tearDown()

    def _callFUT(self, *args, **kwargs):
        from altair.multicheckout.api import get_multicheckout_3d_api
        return get_multicheckout_3d_api(*args, **kwargs)

    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    @mock.patch('altair.multicheckout.impl.Checkout3D')
    def test_without_override_name(self, impl, save_api_response):
        for i in range(0, 3):
            request = DummyRequest()
            request.host = 'x%d.example.com' % i
            impl.return_value.request_card_sales.return_value = i
            service = self._callFUT(request)
            service.checkout_sales('XX0000000000')
            save_api_response.assert_called_with(i)
            impl.called_with(
                u'api-id-%d' % i,
                u'auth-password-%d' % i,
                u'%d' % i,
                u'example.com',
                10
                )

    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    @mock.patch('altair.multicheckout.impl.Checkout3D')
    def test_with_override_name(self, impl, save_api_response):
        for i in range(0, 3):
            request = DummyRequest()
            request.host = 'y%d.example.com' % i
            impl.return_value.request_card_sales.return_value = i
            service = self._callFUT(request, override_name=(u'shop-name-%d' % i))
            service.checkout_sales('XX0000000000')
            save_api_response.assert_called_with(i)
            impl.called_with(
                u'api-id-%d' % i,
                u'auth-password-%d' % i,
                u'%d' % i,
                u'example.com',
                10
                )


