# coding=utf-8
import logging

logger = logging.getLogger(__name__)


class TicketingKeyBaseAuthBackend(object):
    def __init__(self, preset_auth_key, username, membership_name):
        self.preset_auth_key = preset_auth_key
        self.username = username
        self.membership_name = membership_name

    def __call__(self, request, name, opaque):
        from altair.app.ticketing.cart import ICartResource
        from altair.app.ticketing.lots import ILotResource

        logger.debug('opaque=%s, preset_auth_key=%s' % (opaque, self.preset_auth_key))
        auth_key = self.preset_auth_key
        context = getattr(request, 'context', None)
        if context and ICartResource.providedBy(context) or ILotResource.providedBy(context):
            cart_setting = getattr(context, 'cart_setting', None)
            if cart_setting:
                auth_key_from_cart_setting = cart_setting.ticketing_auth_key
                if auth_key_from_cart_setting:
                    auth_key = auth_key_from_cart_setting
        if type(opaque) is dict and opaque.get('key') == auth_key:
            from .plugins.externalmember import EXTERNALMEMBER_AUTH_IDENTIFIER_NAME, EXTERNALMEMBER_ID_POLICY_NAME, \
                EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME
            if name == EXTERNALMEMBER_AUTH_IDENTIFIER_NAME:
                # 外部会員番号取得キーワード認証は、会員番号をUserCredentialのauthz_identifierに
                # メールアドレスを購入者情報のデフォルト表示で使用するのでセットする
                return {
                    'username': self.username,
                    'membership': self.membership_name,
                    'is_guest': False,
                    EXTERNALMEMBER_ID_POLICY_NAME: opaque.get('member_id'),
                    EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME: opaque.get('email_address'),
                }
            return {
                'username': self.username,
                'membership': self.membership_name,
                'is_guest': True,
            }
        else:
            return None
