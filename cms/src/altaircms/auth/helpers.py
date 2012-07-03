# coding: utf-8
import logging
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from pyramid.security import authenticated_userid

from altaircms.models import DBSession
from altaircms.auth.models import Operator, Role
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
        return Operator.query.filter_by(user_id=user_id).filter(Operator.auth_source != "debug").one()
    except NoResultFound:
        logging.warn("operator is not found. so request.user is None")
        return None

@deprecation.deprecate("no more use dummy user")
def get_debug_user(request):
    try:
        return DBSession.query(Operator).filter_by(user_id=1).one() # return debug user if initial data are added
    except NoResultFound:
        role = Role.query.filter(Role.id==1).first()
        return Operator(auth_source="debug",  roles=[role], screen_name=u"debug user")

### use where auth event 

def get_roles_from_role_names(role_names):
    if role_names is not None:
        return Role.query.filter(Role.name.in_(role_names)).order_by(Role.id).all()
    else:
        return []

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
    operator.oauth_token_secret = ''
    operator.roles = roles
    return operator

