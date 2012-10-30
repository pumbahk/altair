from sqlalchemy.orm.exc import NoResultFound
from .models import Host, GlobalSequence

def get_organization(request, override_host=None):
    reg = request.registry
    host_name = override_host or request.host
    try:
        host = Host.query.filter(Host.host_name==host_name).one()
        return host.organization
    except NoResultFound as e:
        raise Exception("Host that named %s is not Found" % host_name)


def get_next_order_no(name="order_no"):
    return GlobalSequence.get_next_value(name)
