from sqlalchemy.orm.exc import NoResultFound
from .models import Host, OrderNoSequence

def get_organization(request, override_host=None):
    reg = request.registry
    host_name = override_host or request.host
    try:
        host = Host.query.filter(Host.host_name==host_name).one()
        return host.organization
    except NoResultFound as e:
        raise Exception("Host that named %s is not Found" % host_name)

def get_host_base_url(request):
    host_name = request.host
    try:
        host = Host.query.filter(Host.host_name==host_name).one()
        base_url = host.base_url
        if base_url is None:
            return "/"
        return base_url
    except NoResultFound as e:
        raise Exception("Host that named %s is not Found" % host_name)

def get_next_order_no(name="order_no"):
    return OrderNoSequence.get_next_value(name)
