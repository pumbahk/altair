# coding: utf-8
import logging
import itertools
from pyramid.security import Allow, Authenticated
from sqlalchemy.orm.exc import NoResultFound
import sqlalchemy.orm as orm
from altaircms.auth.models import Operator, Role, RolePermission

def rolefinder(userid, request):
    """
    ユーザIDを受け取ってロール一覧を返す

    :return: list ユーザのロールリスト
    """
    try:
        operator = Operator.query.filter_by(user_id=userid).one()
        return [role.name for role in operator.roles]
    except NoResultFound, e:
        logging.exception(e)
        return []

def get_acl_candidates():
    # return [(Allow, Authenticated, 'authenticated')] + list(itertools.chain.from_iterable(
    #     [[(Allow, str(role.name), perm) 
    #       for perm in role.permissions] 
    #      for role in Role.query]))
    
    fst = [(Allow, Authenticated, "authenticated")]
    qs = RolePermission.query.filter(Role.id==RolePermission.role_id).options(orm.joinedload("role"))
    filtered = list([(Allow, str(perm.role.name), perm.name) for perm in qs])
    return itertools.chain(fst,  filtered)


# データモデルから取得したACLをまとめる
class RootFactory(object):
    __name__ = None

    def __init__(self, request):
        self.request = request

    def __acl__(self):
        return get_acl_candidates()
                           
