# -*- coding:utf-8 -*-
import logging
import itertools
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.threadlocal import get_current_request
from zope.interface import implementer
from . import api
from ..core import api as core_api
from pyramid.httpexceptions import HTTPNotFound

logger = logging.getLogger(__name__)

class InvalidMemberGroupException(Exception):
    def __init__(self, event_id):
        Exception.__init__(self)
        self.event_id = event_id

@implementer(IAuthorizationPolicy)
class MypageAuthorizationPolicy(object):

    def permits(self, context, principals, permission):
        return "rakuten_auth" in principals

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError

