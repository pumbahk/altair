import unittest
from pyramid import testing
from ..testing import _setup_db, _teardown_db, DummyRequest

class UserApiTest(unittest.TestCase):
    _settings = {'altair.pc.asid': 'test',
                 'altair.mobile.asid': 'test',
                 'altair.smartphone.asid': 'test',
                 'altair.cart.completion_page.temporary_store.cookie_name': '',
                 'altair.cart.completion_page.temporary_store.secret': '',
                }
        
    def setUp(self):
        self.config = testing.setUp(settings=self._settings)
        self.config.include('altair.app.ticketing.cart')
        self.session = _setup_db(['altair.app.ticketing.core.models', 'altair.app.ticketing.users.models'])

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _add_user(self, claimed_id):
        from ..users.models import User, UserCredential, Membership
        user = User()
        membership = Membership(name="rakuten")
        credential = UserCredential(user=user, auth_identifier=claimed_id, membership=membership)
        self.session.add(user)
        self.session.flush()
        return user

    def test_get_or_create_user_create(self):
        from . import api as a
        result = a.get_or_create_user({ 'claimed_id': 'http://example.com/claimed_id' })
        self.assertIsNone(result.id)
        self.assertEqual(result.user_credential[0].auth_identifier, 'http://example.com/claimed_id')
        self.assertEqual(result.user_credential[0].membership.name, 'rakuten')

    def test_get_or_create_user_get(self):
        from . import api as a
        
        user = self._add_user('http://example.com/claimed_id')
        result = a.get_or_create_user({ 'claimed_id': 'http://example.com/claimed_id' })
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.user_credential[0].auth_identifier, 'http://example.com/claimed_id')
        self.assertEqual(result.user_credential[0].membership.name, 'rakuten')

