# coding: utf-8
import logging
import itertools
from pyramid.security import Allow, Authenticated
from sqlalchemy.orm.exc import NoResultFound
import sqlalchemy.orm as orm
from altaircms.auth.models import Operator, Role, RolePermission
from altaircms.modellib import DBSession
from altair.sqlahelper import get_db_session

def rolefinder(userid, request, session=DBSession):
    """
    ユーザIDを受け取ってロール一覧を返す

    :return: list ユーザのロールリスト
    """
    try:
        operator = session.query(Operator).filter_by(user_id=userid).one()
        return [role.name for role in operator.roles]
    except NoResultFound, e:
        logging.exception(e)
        return []

def get_acl_candidates(session=DBSession):
    # return [(Allow, Authenticated, 'authenticated')] + list(itertools.chain.from_iterable(
    #     [[(Allow, str(role.name), perm) 
    #       for perm in role.permissions] 
    #      for role in Role.query]))
    
    fst = [(Allow, Authenticated, "authenticated")]
    qs = session.query(RolePermission).filter(Role.id==RolePermission.role_id).options(orm.joinedload("role"))
    filtered = list([(Allow, str(perm.role.name), perm.name) for perm in qs])
    return itertools.chain(fst,  filtered)


# データモデルから取得したACLをまとめる
class RootFactory(object):
    __name__ = None

    def __init__(self, request):
        self.request = request

    @property
    def __acl__(self):
        return get_acl_candidates(session=get_db_session(self.request, 'slave'))

class OverrideAuthenticationPolicy(object):
    """don't use in app"""
    def __init__(self, i):
        self.i = i

    def unauthenticated_userid(self, request):
        return self.i
