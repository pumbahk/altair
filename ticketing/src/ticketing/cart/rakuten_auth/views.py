# -*- coding:utf-8 -*-
import logging
import pickle

from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.view import view_config
from pyramid import security

from .api import get_open_id_consumer, authenticated_user, remember_user

logger = logging.getLogger(__name__)

class RootView(object):
    def __init__(self, request):
        self.request = request

    @property
    def consumer(self):
        return get_open_id_consumer(self.request)


    def login(self):
        return HTTPUnauthorized()

    def verify(self):
        return HTTPFound(location='/')
        
