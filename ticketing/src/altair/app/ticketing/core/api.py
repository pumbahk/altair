# encoding: utf-8

import logging
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from .models import Host, Organization, OrderNoSequence, ChannelEnum, OrganizationSetting, DBSession
from datetime import datetime

logger = logging.getLogger(__name__)

def refresh_organization(request):
    if hasattr(request, "organization"):
        request.organization = DBSession.merge(request.organization)

def get_organization(request, override_host=None):
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

def get_organization_setting(request, organization, name=OrganizationSetting.DEFAULT_NAME):
    return OrganizationSetting.query.filter(
        OrganizationSetting.organization_id==organization.id, 
        OrganizationSetting.name==name).first()

def is_mobile_request(request):
    return getattr(request, "is_mobile", False)

def get_host_base_url(request):
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

def get_next_order_no(name="order_no"):
    return OrderNoSequence.get_next_value(name)

def get_channel(channel=None, request=None):
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
   
