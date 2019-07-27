# coding=utf-8
import logging
from abc import ABCMeta, abstractmethod

from sqlalchemy.orm.exc import NoResultFound

from altair.app.ticketing.cart.exceptions import NoSalesSegment

logger = logging.getLogger(__name__)


class TicketingKeyAuthAbstractBackend(object):
    """認証のキーを照合する認証方式のBackendの抽象クラス"""
    __metaclass__ = ABCMeta

    def __init__(self, preset_auth_key, username, membership_name):
        self.preset_auth_key = preset_auth_key
        self.username = username
        self.membership_name = membership_name

    @abstractmethod
    def get_identity(self, request, opaque):
        pass

    def __call__(self, request, opaque):
        from altair.app.ticketing.cart.interfaces import ICartResource
        from altair.app.ticketing.lots.interfaces import ILotResource

        logger.debug('opaque=%s, preset_auth_key=%s' % (opaque, self.preset_auth_key))
        context = getattr(request, 'context', None)

        auth_key = self.preset_auth_key
        # カート設定に登録されている認証のキーを取得します。
        if ICartResource.providedBy(context) or ILotResource.providedBy(context):
            cart_setting = getattr(context, 'cart_setting', None)
            if cart_setting and cart_setting.ticketing_auth_key:
                auth_key = cart_setting.ticketing_auth_key

        if type(opaque) is dict and opaque.get('keyword') == auth_key:
            return self.get_identity(request, opaque)
        return None


class PrivateKeyAuthBackend(TicketingKeyAuthAbstractBackend):
    """キーワード認証のBackendクラス。認証のキーが合致していることを検証します。"""
    def get_identity(self, request, opaque):
        return {
            'username': self.username,
            'membership': self.membership_name,
            'is_guest': True,
        }


class ExternalMemberAuthBackend(TicketingKeyAuthAbstractBackend):
    """外部会員番号取得キーワード認証のBackendクラス。
    認証のキーが合致していることを検証して、暗号化されたパラメータを取得します。
    """
    def get_first_membergroup(self, request):
        from altair.app.ticketing.cart.interfaces import ICartResource
        from altair.app.ticketing.lots.interfaces import ILotResource

        context = getattr(request, 'context', None)
        if not context:
            return None

        sales_segment = None
        if ICartResource.providedBy(context):  # カート
            try:
                sales_segment = context.raw_sales_segment
            except (NoSalesSegment, NoResultFound):
                pass
            except Exception as e:
                logger.warning('Failed to find SalesSegment while getting Membergroup linking to it: %s', e)

        elif ILotResource.providedBy(context):  # 抽選
            lot = context.lot
            if not lot:
                return None

            sales_segment = lot.sales_segment

        if not sales_segment:
            return None

        membergroups = sales_segment.membergroups
        if not membergroups:
            return None

        # 販売区分グループには複数の会員区分を結びつけることができますが、全て同じ会員種別に属します。
        # 外部会員番号取得キーワード認証は販売区分に紐づく最初の会員区分と会員種別を認証情報にセットします。
        return membergroups[0]

    def get_identity(self, request, opaque):
        membergroup = self.get_first_membergroup(request)
        if membergroup and membergroup.membership:
            membergroup_name = membergroup.name
            membership_name = membergroup.membership.name
        else:
            membergroup_name = None
            membership_name = self.membership_name

        # 外部会員番号取得キーワード認証は、会員番号をUserCredentialのauthz_identifierに
        # メールアドレスを購入者情報のデフォルト表示で使用するのでセットする
        from .plugins.externalmember import EXTERNALMEMBER_ID_POLICY_NAME, EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME
        return {
            'username': self.username,
            'membergroup': membergroup_name,
            'membership': membership_name,
            'is_guest': False,
            EXTERNALMEMBER_ID_POLICY_NAME: opaque.get('member_id'),
            EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME: opaque.get('email_address'),
        }
