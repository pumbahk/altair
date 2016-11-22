from sqlalchemy.orm.exc import NoResultFound
from altair.sqlahelper import get_db_session
from .models import Operator
from ..models import Organization
from ..utils import generate_salt, digest_secret

def create_operator(request, organization_name, auth_identifier, auth_secret, role):
    salt = generate_salt()
    digest = digest_secret(auth_secret, salt)
    session = get_db_session(request, 'extauth')
    organization = lookup_organization_by_name(request, organization_name)
    operator = Operator(
        organization=organization,
        auth_identifier=auth_identifier,
        auth_secret=digest,
        role=role
        )
    session.add(operator)
    session.flush()
    return operator

def lookup_operator_by_id(request, id):
    if hasattr(request, '_operator_cache'):
        _operator_cache = request._operator_cache
    else:
        _operator_cache = request._operator_cache = {}
    if id in _operator_cache:
        return _operator_cache[id]
    dbsession = get_db_session(request, 'extauth')
    try:
        retval = dbsession.query(Operator) \
            .filter_by(id=id) \
            .one()
        _operator_cache[id] = retval
        return retval
    except NoResultFound:
        return None

def lookup_operator_by_auth_identifier(request, auth_identifier):
    dbsession = get_db_session(request, 'extauth')
    try:
        return dbsession.query(Operator) \
            .filter_by(auth_identifier=auth_identifier) \
            .one()
    except NoResultFound:
        return None

def lookup_operator_by_credentials(request, auth_identifier, auth_secret):
    try:
        operator = lookup_operator_by_auth_identifier(request, auth_identifier)
        if operator is not None:
            digest = digest_secret(auth_secret, operator.auth_secret[0:32])
            if operator.auth_secret != digest:
                return None
        return operator
    except NoResultFound:
        return None

def lookup_organization_by_name(request, organization_name):
    session = get_db_session(request, 'extauth')
    try:
        organization = session.query(Organization).filter_by(short_name=organization_name).one()
    except NoResultFound as e:
        raise e
    except MultipleResultsFound as e:
        raise e

    return organization

def lookup_organization_by_id(request, organization_id):
    session = get_db_session(request, 'extauth')
    try:
        organization = session.query(Organization).filter_by(id=organization_id).one()
    except NoResultFound as e:
        raise e

    return organization
