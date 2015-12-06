# encoding: utf-8
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import instance_state
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.session import make_transient
from altair.sqlahelper import get_db_session
from altair.app.ticketing.extauth  import models
from altair.app.ticketing.security import get_extra_auth_info_from_principals
from pyramid.security import Everyone

ENV_ORGANIZATION_ID_KEY = 'altair.app.ticketing.extauth.organization_id'
ENV_ORGANIZATION_PATH_KEY = 'altair.app.ticketing.extauth.organization_path'

def get_organization(request):
    session = get_db_session(request, 'extauth_slave')
    try:
        organization = session.query(models.Organization) \
            .join(models.Host, models.Organization.id == models.Host.organization_id) \
            .filter(models.Host.host_name == unicode(request.host)) \
            .one()
    except (NoResultFound, MultipleResultsFound) as e:
        raise Exception("Host that named %s is not Found" % request.host)
    make_transient(organization)
    return organization

def includeme(config):
    from datetime import datetime
    config.add_request_method(get_organization, 'organization', reify=True)
    config.add_request_method(lambda request: datetime.now(), 'now', reify=True)
