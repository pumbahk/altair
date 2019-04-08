# coding=utf-8
import base64
import logging

from pyramid.httpexceptions import HTTPForbidden

from altair.app.ticketing.utils import Crypto
from .backends import TicketingKeyBaseAuthBackend
from .plugins.externalmember import ExternalMemberAuthPlugin, EXTERNALMEMBER_AUTH_IDENTIFIER_NAME
from .plugins.privatekey import PrivateKeyAuthPlugin, PRIVATEKEY_AUTH_IDENTIFIER_NAME
from .views import PrivateKeyAuthView, ExternalMemberAuthView

logger = logging.getLogger(__name__)


def add_externalmember_auth_cipher(config):
    settings = config.registry.settings
    pub_key = settings.get('altair.ticketing.authentication.externalmember.cipher.pub_key')
    iv = settings.get('altair.ticketing.authentication.externalmember.cipher.iv')

    from binascii import unhexlify
    crypto = Crypto(unhexlify(pub_key), unhexlify(iv))

    def externalmember_auth_encrypt(request, data):
        try:
            encrypted = crypto.encrypt(data)
            return base64.b64encode(encrypted)
        except Exception as e:
            logger.warn('Failed to encrypt %s: %s', data, e.message)
            raise HTTPForbidden()

    def externalmember_auth_decrypt(request, data):
        try:
            decoded = base64.b64decode(data)
            return crypto.decrypt(decoded)
        except Exception as e:
            logger.warn('Failed to decrypt %s: %s', data, e.message)
            raise HTTPForbidden()

    config.add_request_method(externalmember_auth_encrypt)
    config.add_request_method(externalmember_auth_decrypt)


def add_ticketing_auth_plugin_entrypoints(config, route_name):
    config.add_view(
        view=ExternalMemberAuthView,
        request_method='POST',
        request_param=('keyword', 'email_address', 'member_id'),
        route_name=route_name,
    )
    config.add_view(
        view=PrivateKeyAuthView,
        request_method='POST',
        request_param='keyword',
        route_name=route_name,
    )


def includeme(config):
    from altair.app.ticketing.authentication import config as auth_config
    config.add_directive('add_challenge_view', auth_config.add_challenge_view, action_wrap=True)

    settings = config.registry.settings

    # 外部会員番号取得キーワード認証
    backend = TicketingKeyBaseAuthBackend(
        preset_auth_key=settings.get('altair.ticketing.authentication.externalmember.key'),
        username=settings.get('altair.ticketing.authentication.externalmember.username', '::externalmember::'),
        membership_name=settings.get('altair.ticketing.authentication.externalmember.membership', 'externalmember'),
    )
    config.add_auth_plugin(ExternalMemberAuthPlugin(backend))

    # キーワード認証
    backend = TicketingKeyBaseAuthBackend(
        preset_auth_key=settings.get('altair.ticketing.authentication.privatekey.key'),
        username=settings.get('altair.ticketing.authentication.privatekey.username', '::privatekey::'),
        membership_name=settings.get('altair.ticketing.authentication.privatekey.membership', 'privatekey'),
    )
    config.add_auth_plugin(PrivateKeyAuthPlugin(backend))

    # AES128-CBC方式の暗号化・復号化メソッドを登録
    add_externalmember_auth_cipher(config)

    # 認証のviewを登録
    config.add_directive('add_ticketing_auth_plugin_entrypoints', add_ticketing_auth_plugin_entrypoints)

