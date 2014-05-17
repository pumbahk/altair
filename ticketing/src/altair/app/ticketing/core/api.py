# encoding: utf-8

import logging
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from ..utils import sensible_alnum_encode

logger = logging.getLogger(__name__)

def refresh_organization(request):
    if hasattr(request, "organization"):
        request.organization = DBSession.merge(request.organization)

def get_organization(request, override_host=None):
    from .models import Host, Organization
    if hasattr(request, 'organization'):
        organization_id = request.environ.get('altair.app.ticketing.cart.organization_id')
        organization_path = request.environ.get('altair.app.ticketing.cart.organization_path')
        logger.debug("organization_id = %s organization_path = %s" % (organization_id, organization_path))
        return request.organization

    host_name = override_host or request.host
    try:
        host = Host.query.options(
            joinedload(Host.organization),
            joinedload(Host.organization,
                       Organization.settings),
        ).filter(
            Host.host_name==unicode(host_name)
        ).one()
        request.organization = host.organization
        request.environ['altair.app.ticketing.cart.organization_id'] = request.organization.id
        return request.organization
    except NoResultFound as e:
        raise Exception("Host that named %s is not Found" % host_name)

def get_organization_setting(request, organization, name=None):
    from .models import OrganizationSetting
    if name is None:
        name = OrganizationSetting.DEFAULT_NAME
    return OrganizationSetting.query.filter(
        OrganizationSetting.organization_id==organization.id, 
        OrganizationSetting.name==name).first()

def is_mobile_request(request):
    return getattr(request, "is_mobile", False)

def get_host_base_url(request):
    from .models import Host
    host_name = request.host
    try:
        host = Host.query.filter(Host.host_name==host_name).one()
        if is_mobile_request(request):
            base_url = host.mobile_base_url or "/"
        else:
            base_url = host.base_url or "/"
        return base_url
    except NoResultFound as e:
        raise Exception("Host that named %s is not Found" % host_name)

def get_next_order_no(request, organization, name="order_no"):
    from .models import OrderNoSequence
    base_id = OrderNoSequence.get_next_value(name)
    return organization.code + sensible_alnum_encode(base_id).zfill(10)

def get_channel(channel=None, request=None):
    from .models import ChannelEnum
    for c in ChannelEnum:
        if c.v == channel:
            return c

    if request and hasattr(request, 'is_mobile') and request.is_mobile:
        return ChannelEnum.Mobile
    else:
        return ChannelEnum.PC

def delete_event(event):
    # 既に販売されている場合は削除できない
    if event.sales_start_on and event.sales_start_on < datetime.now():
        raise Exception(u'既に販売開始日時を経過している為、削除できません')
    event.delete()

def get_default_contact_url(request, organization, carrier):
    contact_url = None
    if carrier.is_nonmobile:
        contact_url = organization.setting.contact_pc_url
    else:
        contact_url = organization.setting.contact_mobile_url
    # XXX: デフォルトが default_mail_sender なのは良くないけど一応仕様ということに
    if contact_url is None and organization.setting.default_mail_sender is not None:
        contact_url = u'mailto:%s' % organization.setting.default_mail_sender
    return contact_url

def iterate_serial_and_seat(ordered_product_item_like):
    if ordered_product_item_like.seats:
        for i, s in enumerate(ordered_product_item_like.seats):
            yield i, s
    else:
        for i in range(ordered_product_item_like.quantity):
            yield i, None

def calculate_total_amount(order_like):
    if not order_like.sales_segment:
        return None
    return order_like.sales_segment.get_amount(
        order_like.payment_delivery_pair,
        [(p.product, p.price, p.quantity) for p in order_like.items])
