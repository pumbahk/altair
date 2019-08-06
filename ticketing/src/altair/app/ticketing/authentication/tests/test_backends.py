# coding=utf-8
import unittest

from altair.app.ticketing.authentication.backends import PrivateKeyAuthBackend, ExternalMemberAuthBackend
from altair.app.ticketing.authentication.plugins.externalmember import EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME, \
    EXTERNALMEMBER_ID_POLICY_NAME
from altair.app.ticketing.cart.interfaces import ICartResource
from altair.app.ticketing.lots.interfaces import ILotResource
from pyramid import testing


class TicketingKeyBaseAuthBackendTest(unittest.TestCase):
    DECRYPTED_EXTERNALMEMBER_AUTH_PARAM = {
        'keyword': 'testKey',
        'email_address': 'test@example.com',
        'member_id': '100',
    }

    def setUp(self):
        self.request = testing.DummyRequest()
        self.privatekey_auth_backend = \
            PrivateKeyAuthBackend(preset_auth_key='', username='::privatekey::', membership_name='privatekey')
        self.externalmember_auth_backed = \
            ExternalMemberAuthBackend(preset_auth_key='',
                                      username='::externalmember::',
                                      membership_name='externalmember')

    def test_privatekey_auth_identity_returned(self):
        backend = self.privatekey_auth_backend
        opaque = {
            'keyword': 'testKey'
        }
        self.request.context = testing.DummyResource(
            __provides__=ICartResource,
            cart_setting=testing.DummyModel(
                ticketing_auth_key='testKey'
            )
        )
        identity = backend(self.request, opaque)

        self.assertEqual(backend.username, identity.get('username'))
        self.assertEqual(backend.membership_name, identity.get('membership'))
        self.assertTrue(identity.get('is_guest'))

    def _assert_externalmember_identity(self, identity, membership, membergroup):
        self.assertEqual(self.externalmember_auth_backed.username, identity.get('username'))
        self.assertEqual(membership, identity.get('membership'))
        self.assertEqual(membergroup, identity.get('membergroup'))
        self.assertFalse(identity.get('is_guest'))
        # 外部会員番号取得キーワード認証はメールアドレスと会員番号もidentityにセットする
        self.assertEqual(self.DECRYPTED_EXTERNALMEMBER_AUTH_PARAM.get('email_address'),
                         identity.get(EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME))
        self.assertEqual(self.DECRYPTED_EXTERNALMEMBER_AUTH_PARAM.get('member_id'),
                         identity.get(EXTERNALMEMBER_ID_POLICY_NAME))

    def test_externalmember_auth_identity_returned(self):
        backend = self.externalmember_auth_backed
        self.request.context = testing.DummyResource(
            __provides__=ICartResource,
            cart_setting=testing.DummyModel(
                ticketing_auth_key='testKey'
            )
        )
        identity = backend(self.request, self.DECRYPTED_EXTERNALMEMBER_AUTH_PARAM)
        self._assert_externalmember_identity(identity, self.externalmember_auth_backed.membership_name, None)

    def test_externalmember_auth_identity_returned_linking_to_membership(self):
        backend = self.externalmember_auth_backed
        cart_setting = testing.DummyModel(ticketing_auth_key='testKey')
        membergroups = [
            testing.DummyModel(name='testMemberGroup', membership=testing.DummyModel(name='testMembership'))
        ]

        # カート
        self.request.context = testing.DummyResource(
            __provides__=ICartResource,
            cart_setting=cart_setting,
            raw_sales_segment=testing.DummyModel(membergroups=membergroups)
        )
        identity = backend(self.request, self.DECRYPTED_EXTERNALMEMBER_AUTH_PARAM)
        self._assert_externalmember_identity(identity, 'testMembership', 'testMemberGroup')

        # 抽選
        self.request.context = testing.DummyResource(
            __provides__=ILotResource,
            cart_setting=cart_setting,
            lot=testing.DummyModel(sales_segment=testing.DummyModel(membergroups=membergroups))
        )
        identity = backend(self.request, self.DECRYPTED_EXTERNALMEMBER_AUTH_PARAM)
        self._assert_externalmember_identity(identity, 'testMembership', 'testMemberGroup')

    def test_identity_not_found(self):
        backend = self.externalmember_auth_backed
        # 取得するキーが存在しない場合は None を返却する
        identity = backend(self.request, opaque={})

        self.assertIsNone(identity)
