from unittest import TestCase
from pyramid import testing 
import mock

class RegressionTest(TestCase):
    def setUp(self):
        config = testing.setUp()
        config.include('.'.join(__name__.split('.')[0:-1]))
        self.config = config

    def tearDown(self):
        testing.tearDown()

    def test_detect_from_email_address(self):
        from .api import detect_from_email_address
        from .carriers import NonMobile, DoCoMo
        self.assertEqual(
            detect_from_email_address(self.config.registry, 'test@example.com'),
            NonMobile)
        self.assertEqual(
            detect_from_email_address(self.config.registry, 'test@docomo.ne.jp'),
            DoCoMo)


class MobileRequestMakerTest(TestCase):
    def _getTarget(self):
        from .impl import MobileRequestMaker
        return MobileRequestMaker

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_revalidate_session1(self):
        import hashlib
        request = mock.MagicMock()
        request.user_agent = 'USER_AGENT'
        request.session.get.return_value = hashlib.sha1('USER_AGENT').hexdigest()
        target = self._makeOne()
        target.revalidate_session(request)
        request.session.get.assert_called_with_argument('altair.mobile.impl.us_hash')
        request.session.invalidate.assert_not_called()

    def test_revalidate_session2(self):
        import hashlib
        request = mock.MagicMock()
        request.user_agent = 'USER_AGENT'
        request.session.get.return_value = hashlib.sha1('OOPS').hexdigest()
        target = self._makeOne()
        target.revalidate_session(request)
        request.session.get.assert_called_with_argument('altair.mobile.impl.us_hash')
        request.session.invalidate.assert_called()

