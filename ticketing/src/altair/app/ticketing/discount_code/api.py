# encoding: utf-8
from sqlalchemy.orm.exc import NoResultFound
from .models import DiscountCodeSetting


def is_enabled_discount_code_checked(context, request):
    """
    クーポン・割引コードの使用設定がONになっているか確認
    requestは使用できていないが、使用場所がcustom_predicatesのために必要。
    """
    return context.user.organization.setting.enable_discount_code


def get_discount_setting(context, request):
    """DiscountCodeSettingとそれに紐づくDiscountCodeのレコードの取得"""
    setting_id = request.matchdict['setting_id']

    query = context.session.query(DiscountCodeSetting).filter_by(
        organization_id=context.user.organization_id,
        id=setting_id
    )

    try:
        context.setting = query.one()
        return True
    except NoResultFound:
        return False

