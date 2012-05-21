# coding: utf-8
import logging
from sqlalchemy.orm.exc import NoResultFound
from pyramid.security import authenticated_userid

from altaircms.models import DBSession
from altaircms.auth.models import Operator

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
    try:
        return DBSession.query(Operator).filter_by(user_id=authenticated_userid(request)).one()
    except NoResultFound:
        logging.warn("operator is not found. so request.user is None")
        return None


def get_debug_user(request):
    try:
        return DBSession.query(Operator).filter_by(user_id=1).one() # return debug user iff initial data are added
    except NoResultFound:
        return Operator(auth_source="debug", user_id=1, id=1, role_id=1, screen_name=u"debug user")

# def user_context(event):
#     """
#     テンプレートでレンダリングするためのユーザオブジェクトを返す
#     """
#     user = None
#     try:
#         request = event['request']
#         if not hasattr(request, "session"):
#             return None
#         user = DBSession.query(Operator).filter_by(user_id=authenticated_userid(request)).one()
#     except NoResultFound, e:
#         pass

#     return user
