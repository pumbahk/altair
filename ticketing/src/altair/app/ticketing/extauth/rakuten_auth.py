# coding=utf-8
import logging
import re

from zope.interface import implementer
from altair.rakuten_auth.interfaces import IRakutenOpenIDURLBuilder
from urlparse import urljoin

logger = logging.getLogger(__name__)

PREFIX = 'altair.rakuten_auth.claimed_id:'

def get_openid_claimed_id(request):
    for principal in request.effective_principals:
        if principal.startswith(PREFIX):
            return principal[len(PREFIX):]
    return None

def add_claimed_id_to_principals(identities, request):
    if 'rakuten' in identities:
        return ['%s%s' % (PREFIX, identities['rakuten']['claimed_id'])]
    return []

def get_rakuten_auth_setting(request, k):
    settings = request.organization.settings
    if settings is not None:
        rakuten_auth_settings = settings.get(u'rakuten_auth')
        if rakuten_auth_settings is not None:
            return rakuten_auth_settings.get(k)
    return None

def consumer_key_builder(request):
    return get_rakuten_auth_setting(request, u'oauth_consumer_key')

def consumer_secret_builder(request):
    return get_rakuten_auth_setting(request, u'oauth_consumer_secret')


def get_open_id_for_sso(request):
    """
    リクエストに Ts Cookie がある場合は復号化して Open ID を取得する。
    :param request: リクエスト
    :return: 復号化に成功した場合は Open ID, それ以外は None
    """
    ts = request.cookies.get('Ts')
    if ts is None:
        return None

    # Ts Cookie は先頭 16 byte が IV で、その後は暗号化された Open ID
    iv, encrypted = ts[:16], ts[16:]

    if len(iv) != 16 or re.match(r'^\s*$', encrypted):
        return None

    import base64
    from Crypto.Cipher import AES
    try:
        # 復号化手順
        # Base64 デコード -> AES-128 CBC 方式で復号化 -> パディングを除く
        decoded = base64.b64decode(encrypted)

        key = request.registry.settings.get('altair.rakuten_sso.ts.encryption_key')
        cipher = AES.new(key=key, mode=AES.MODE_CBC, IV=iv)

        decrypted = cipher.decrypt(decoded)
        open_id = decrypted[:-ord(decrypted[len(decrypted) - 1:])]
        if open_id == '':
            return None

        logger.debug('Ts Cookie decrypted successfully for SSO login (Open ID: %s)', open_id)

        return open_id
    except Exception as e:
        logger.warn('[SSO0001] Failed to decrypt Ts cookie %s and get Open ID: %s', ts, e)
        return None


@implementer(IRakutenOpenIDURLBuilder)
class OrganizationSettingsBasedRakutenAuthURLBuilder(object):
    def __init__(self, **kwargs):
        pass

    def extra_verify_url_exists(self, request):
        return get_rakuten_auth_setting(request, u'proxy_url_pattern') is not None

    def build_base_url(self, request):
        proxy_url_pattern = get_rakuten_auth_setting(request, u'proxy_url_pattern')
        subdomain = request.host.split('.', 1)[0]
        return proxy_url_pattern.format(
            subdomain=subdomain
            )

    def build_return_to_url(self, request):
        if self.extra_verify_url_exists(request):
            return urljoin(self.build_base_url(request).rstrip('/') + '/', request.route_path('rakuten_auth.verify').lstrip('/'))
        else:
            return request.route_url('rakuten_auth.verify')

    def build_error_to_url(self, request):
        if self.extra_verify_url_exists(request):
            return urljoin(self.build_base_url(request).rstrip('/') + '/', request.route_path('rakuten_auth.error').lstrip('/'))
        else:
            return request.route_url('rakuten_auth.error')

    def build_verify_url(self, request):
        return request.route_url('rakuten_auth.verify')

    def build_extra_verify_url(self, request):
        if self.extra_verify_url_exists(request):
            return request.route_url('rakuten_auth.verify2')
        else:
            return None
