# encoding: utf-8

from altair.app.ticketing.core.models import OrganizationSetting
from sqlalchemy.orm.exc import NoResultFound


def is_enabled_discount_code_checked(context, request):
    """クーポン・割引コードの使用設定がONになっているか確認"""
    organization_id = context.user.organization.id
    try:
        context.session.query(OrganizationSetting) \
            .filter_by(organization_id=organization_id, enable_discount_code=1) \
            .one()
    except NoResultFound:
        return False

    return True
