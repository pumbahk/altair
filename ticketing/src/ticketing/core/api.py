from sqlalchemy.orm.exc import NoResultFound
from .models import Host, OrderNoSequence, ChannelEnum

def get_organization(request, override_host=None):
    reg = request.registry
    host_name = override_host or request.host
    try:
        host = Host.query.filter(Host.host_name==unicode(host_name)).one()
        return host.organization
    except NoResultFound as e:
        raise Exception("Host that named %s is not Found" % host_name)

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
