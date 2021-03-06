# coding=utf-8
import logging

from pyramid.httpexceptions import HTTPFound

from altair.app.ticketing.utils import Crypto
from .backends import ExternalMemberAuthBackend, PrivateKeyAuthBackend
from .interfaces import IExternalMemberAuthCrypto
from .plugins.externalmember import ExternalMemberAuthPlugin, EXTERNALMEMBER_AUTH_IDENTIFIER_NAME, \
    ExternalMemberAuthPredicate
from .plugins.privatekey import PrivateKeyAuthPlugin, PRIVATEKEY_AUTH_IDENTIFIER_NAME, PrivateKeyAuthPredicate

logger = logging.getLogger(__name__)


def add_ticketing_auth_plugin_entrypoints(config, route_name):
    config.add_view(
        view=lambda request: HTTPFound(request.current_route_path()),
        request_method='POST',
        externalmember_auth_param=('keyword', 'member_id'),
        route_name=route_name,
    )
    config.add_view(
        view=lambda request: HTTPFound(request.current_route_path()),
        request_method='POST',
        privatekey_auth_param='keyword',
        route_name=route_name,
    )


def add_challenge_view(config):
    """viewに認証クラスをAdapterとして登録します"""
    from altair.app.ticketing.authentication import config as auth_config
    config.add_directive('add_challenge_view', auth_config.add_challenge_view, action_wrap=True)


def includeme(config):
    add_challenge_view(config)

    settings = config.registry.settings

    # 外部会員番号取得キーワード認証
    backend = ExternalMemberAuthBackend(
        preset_auth_key=settings.get('altair.ticketing.authentication.externalmember.key'),
        username=settings.get('altair.ticketing.authentication.externalmember.username', '::externalmember::'),
        membership_name=settings.get('altair.ticketing.authentication.externalmember.membership', 'externalmember'),
    )
    config.add_auth_plugin(ExternalMemberAuthPlugin(backend))

    # キーワード認証
    backend = PrivateKeyAuthBackend(
        preset_auth_key=settings.get('altair.ticketing.authentication.privatekey.key'),
        username=settings.get('altair.ticketing.authentication.privatekey.username', '::privatekey::'),
        membership_name=settings.get('altair.ticketing.authentication.privatekey.membership', 'privatekey'),
    )
    config.add_auth_plugin(PrivateKeyAuthPlugin(backend))

    pub_key = settings.get('altair.ticketing.authentication.externalmember.cipher.pub_key')
    iv = settings.get('altair.ticketing.authentication.externalmember.cipher.iv')

    # AES128-CBC方式の暗号化・復号化メソッドを登録
    from binascii import unhexlify
    crypto = Crypto(unhexlify(pub_key), unhexlify(iv))
    config.registry.registerUtility(crypto, IExternalMemberAuthCrypto)

    # 認証のviewを登録
    config.add_view_predicate('externalmember_auth_param', ExternalMemberAuthPredicate)
    config.add_view_predicate('privatekey_auth_param', PrivateKeyAuthPredicate)
    config.add_directive('add_ticketing_auth_plugin_entrypoints', add_ticketing_auth_plugin_entrypoints)
