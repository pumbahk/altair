# encoding: utf-8
from sqlalchemy.orm.exc import NoResultFound
from .models import DiscountCodeSetting, UsedDiscountCode


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


def calc_discount_amount(order_like):
    # order_likeには、cartと、_DummyCartが入る想定
    discount_amount = 0
    for item in order_like.items:
        for element in item.elements:
            for index in range(element.quantity):
                used_code = UsedDiscountCode.query.filter(UsedDiscountCode.carted_product_item_id == element.id).first()
                if used_code:
                    discount_amount = discount_amount + element.product_item.price
    return discount_amount
