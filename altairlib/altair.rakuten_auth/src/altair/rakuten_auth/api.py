# -*- coding:utf-8 -*-

import urllib
import urllib2
import pickle
import urlparse
import time
import uuid
import hashlib
import logging
import random

from datetime import datetime
from zope.interface import implementer
from pyramid import security
from pyramid.interfaces import IRequest

from .interfaces import IRakutenOpenID, IRakutenOAuth, IRakutenIDAPIFactory, IRakutenIDAPI2Factory

from .events import Authenticated

logger = logging.getLogger(__name__)

def gen_reseve_no(order_no):
    base = "%012d" % order_no
    r = random.randint(0, 1000)
    base += "%03d" % r
    return base + checkdigit(base)

def checkdigit(numbers):
    numbers = list(reversed(numbers))
    evens = 0
    for n in numbers[::2]:
        evens += int(n)

    odds = 0
    for n in numbers[1::2]:
        odds += int(n)

    check = 10 - (evens * 3 + odds) % 10
    if check == 10:
        check = 0
    return str(check)

def get_rakuten_oauth(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IRakutenOAuth)

def get_rakuten_id_api_factory(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IRakutenIDAPIFactory)

def get_rakuten_id_api2_factory(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IRakutenIDAPI2Factory)

