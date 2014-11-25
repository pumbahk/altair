# encoding: utf-8
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import instance_state
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import make_transient
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.security import get_extra_auth_info_from_principals

ENV_ORGANIZATION_ID_KEY = 'altair.app.ticketing.cart.organization_id'
ENV_ORGANIZATION_PATH_KEY = 'altair.app.ticketing.cart.organization_path'

def get_organization(request):
    override_organization_id = request.environ.get(ENV_ORGANIZATION_ID_KEY)

    if hasattr(request, '_resolved_organization'):
        assert instance_state(request._resolved_organization).session_id is None
        if override_organization_id is None or request._resolved_organization.id == override_organization_id:
            return request._resolved_organization

    session = get_db_session(request, 'slave')
    try:
        if override_organization_id is not None:
            organization = session.query(c_models.Organization) \
                .options(joinedload(c_models.Organization.settings)) \
                .filter(c_models.Organization.id == override_organization_id) \
                .one()
        else:
            organization = session.query(c_models.Organization) \
                .options(joinedload(c_models.Organization.settings)) \
                .join(c_models.Organization.hosts) \
                .filter(c_models.Host.host_name == unicode(request.host)) \
                .one()
    except NoResultFound as e:
        raise Exception("Host that named %s is not Found" % request.host)
    make_transient(organization)
    if override_organization_id is None:
        request.organization = organization
        request.environ[ENV_ORGANIZATION_ID_KEY] = request.organization.id
    return organization

# XXX: 互換性のために変にごちゃごちゃしている
def get_altair_auth_info(request):
    retval = {}
    user_id = request.authenticated_userid
    principals = request.effective_principals
    if principals:
        extra = get_extra_auth_info_from_principals(principals)
        retval.update(extra)
        retval['user_id'] = user_id
        if extra['auth_type'] == 'rakuten':
            retval['claimed_id'] = retval['auth_identifier'] = user_id
            retval['membership'] = 'rakuten'
        elif extra['auth_type']:
            retval['username'] = retval['auth_identifier'] = user_id
        else:
            # auth_type が無いときは guest と見なす
            retval['is_guest'] = True
            retval['auth_identifier'] = None
            retval['membership'] = None
    else:
        retval['is_guest'] = True
        retval['user_id'] = None
        retval['auth_identifier'] = None
        retval['membership'] = None
    retval['organization_id'] = request.organization.id
    return retval

def includeme(config):
    config.add_request_method(get_organization, 'organization', reify=True)
    config.add_request_method(get_altair_auth_info, 'altair_auth_info', reify=True)

