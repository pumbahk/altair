# coding: utf-8
import logging
from pyramid.security import Allow, Authenticated
from sqlalchemy.orm.exc import NoResultFound

from altaircms.models import DBSession
from altaircms.auth.models import Operator, Role

from zope.interface import implements
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.location import lineage
from pyramid.security import ACLAllowed
import itertools


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


# データモデルから取得したACLをまとめる
class RootFactory(object):
    __name__ = None

    def __init__(self, request):
        self.request = request

    @property
    def __acl__(self):
        return [(Allow, Authenticated, 'authenticated')] + list(itertools.chain.from_iterable(
            [[(Allow, str(role.name), perm) 
              for perm in role.permissions] 
             for role in Role.query]))


class SecurityAllOK(list):
    def __init__(self):
        from altaircms.auth.models import DEFAULT_ROLE
        self.roles = [DEFAULT_ROLE]
        
    def __call__(self, user_id, request):
        return self.roles


