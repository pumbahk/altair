# coding: utf-8
from pyramid.security import authenticated_userid

from sqlalchemy.orm.exc import NoResultFound

from altaircms.models import DBSession
from altaircms.auth.models import Operator


def user_context(event):
    """
    テンプレートでレンダリングするためのユーザオブジェクトを返す
    """
    user = None

    try:
        user = DBSession.query(Operator).filter_by(user_id=authenticated_userid(event['request'])).one()
    except NoResultFound, e:
        pass

    return user
