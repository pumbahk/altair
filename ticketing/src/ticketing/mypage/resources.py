# -*- coding:utf-8 -*-

"""

TODO: 引き当て処理自体はResourceから分離する。
TODO: cart取得
"""

from datetime import datetime
import itertools
from sqlalchemy import sql
from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow

from . import logger

class TicketingMyPageResources(object):
    __acl__ = [
        (Allow, Authenticated, 'view'),
    ]

    def __init__(self, request):
        self.request = request