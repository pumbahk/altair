# coding: utf-8
import logging
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from pyramid.security import authenticated_userid

from altaircms.models import DBSession
from altaircms.auth.models import Operator
from altaircms.auth.models import Role
from altaircms.auth.models import Organization
from zope.deprecation import deprecation

logger = logging.getLogger(__file__)

def with_log(r):
    logging.info("========================================")
    logger.info(r)
    logging.info("========================================")
    return r


def get_authenticated_user(request):
    """
    認証済みのuserオブジェクトを返す。存在しない場合にはNoneを返す
    """
    user_id = authenticated_userid(request)
    logger.debug("*authenticate* user_id = %s" % user_id)
    try:
        return Operator.query.filter_by(user_id=user_id).one()
    except NoResultFound:
        logging.warn("operator is not found. so request.user is None")
        return None

def get_authenticated_organization(request):
    """
    認証済みのorganizationオブジェクトを返す。存在しない場合にはNoneを返す
    """
    if hasattr(request, "user"):
        return request.user.organization if request.user else None
    raise NotImplementedError




### use where auth event 
def get_roles_from_role_names(role_names):
    if role_names is not None:
        return Role.query.filter(Role.name.in_(role_names)).order_by(Role.id).all()
    else:
        return []

def get_or_create_organization(source, organization_id, organization_name):
    organization = Organization.query.filter_by(backend_id=organization_id, auth_source=source).first()
    if organization is None:
        logger.info("*login* organization is not found. create it")
        organization = Organization(backend_id=organization_id, name=organization_name, 
                                    auth_source=source)
        created_data = dict(backend_id=organization_id, name=organization_name, 
                            auth_source=source)
        logger.info("*login* created organization: %s" % created_data)
    return organization

def get_or_create_operator(source, user_id, screen_name):
    operator = Operator.query.filter_by(auth_source=source, user_id=user_id).first()
    if operator is None:
        logger.info("*login* operator is not found. create it")
        operator = Operator(auth_source=source, user_id=user_id, screen_name=screen_name)

        created_data = dict(auth_source=source, user_id=user_id, screen_name=screen_name)
        logger.info("*login* created operator: %s" % created_data)
    return operator

def update_operator_with_data(operator, roles, data):
    operator.last_login = datetime.now()
    operator.screen_name = data['screen_name']
    operator.oauth_token = data['access_token']
    operator.oauth_token_secret = ''##?
    operator.roles = roles
    return operator
