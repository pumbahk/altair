# coding: utf-8
from pyramid.security import authenticated_userid

from sqlalchemy.orm.exc import NoResultFound

from altaircms.models import DBSession
from altaircms.auth.models import Operator


def get_authenticated_user(request):
    """
    認証済みのuserオブジェクトを返す。存在しない場合にはNoneを返す
    """
    user = None
    try:
        if not hasattr(request, "session"):
            return None
        user = DBSession.query(Operator).filter_by(user_id=authenticated_userid(request)).one()
    except NoResultFound:
        pass
    return user

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
