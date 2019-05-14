# coding=utf-8
import unittest

from altair.app.ticketing.authentication.backends import TicketingKeyBaseAuthBackend
from altair.app.ticketing.authentication.plugins.externalmember import EXTERNALMEMBER_AUTH_IDENTIFIER_NAME, \
    EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME, EXTERNALMEMBER_ID_POLICY_NAME
from altair.app.ticketing.authentication.plugins.privatekey import PRIVATEKEY_AUTH_IDENTIFIER_NAME
from altair.app.ticketing.cart import ICartResource
from pyramid import testing


class TicketingKeyBaseAuthBackendTest(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()

    def test_privatekey_auth_identity_returned(self):
        backend = TicketingKeyBaseAuthBackend(preset_auth_key='',
                                              username='::privatekey::',
                                              membership_name='privatekey')
        opaque = {
            'keyword': 'testKey'
        }
        self.request.context = testing.DummyResource(
            __provides__=ICartResource,
            cart_setting=testing.DummyModel(
                ticketing_auth_key='testKey'
            )
        )
        identity = backend(self.request, PRIVATEKEY_AUTH_IDENTIFIER_NAME, opaque)

        self.assertEqual(backend.username, identity.get('username'))
        self.assertEqual(backend.membership_name, identity.get('membership'))
        self.assertTrue(identity.get('is_guest'))

    def test_externalmember_auth_identity_returned(self):
        backend = TicketingKeyBaseAuthBackend(preset_auth_key='',
                                              username='::externalmember::',
                                              membership_name='externalmember')
        opaque = {
            'keyword': 'testKey',
            'email_address': 'test@example.com',
            'member_id': '100',
        }
        self.request.context = testing.DummyResource(
            __provides__=ICartResource,
            cart_setting=testing.DummyModel(
                ticketing_auth_key='testKey'
            )
        )
        identity = backend(self.request, EXTERNALMEMBER_AUTH_IDENTIFIER_NAME, opaque)

        self.assertEqual(backend.username, identity.get('username'))
        self.assertEqual(backend.membership_name, identity.get('membership'))
        self.assertFalse(identity.get('is_guest'))
        # 外部会員番号取得キーワード認証はメールアドレスと会員番号もidentityにセットする
        self.assertEqual(opaque.get('email_address'),
                         identity.get(EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME))
        self.assertEqual(opaque.get('member_id'),
                         identity.get(EXTERNALMEMBER_ID_POLICY_NAME))

    def test_identity_not_found(self):
        backend = TicketingKeyBaseAuthBackend(preset_auth_key='',
                                              username='::externalmember::',
                                              membership_name='externalmember')

        # 取得するキーが存在しない場合は None を返却する
        identity = backend(self.request, EXTERNALMEMBER_AUTH_IDENTIFIER_NAME, opaque={})

        self.assertIsNone(identity)
