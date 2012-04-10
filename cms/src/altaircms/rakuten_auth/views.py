# -*- coding:utf-8 -*-
import logging
import pickle

from pyramid.httpexceptions import HTTPFound
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
        url = self.consumer.get_redirect_url()
        logger.debug('openid redirect: %s' % url)
        return HTTPFound(location=url)

    def verify(self):
        logger.debug("verify %s" % self.request.url)

        response = HTTPFound(location=self.request.route_url('top'))
        clamed_url = self.consumer.verify_authentication(self.request)
        if clamed_url:
            user_data = {'clamed_url': clamed_url}
            headers = remember_user(self.request, user_data)

            response.headerlist.extend(headers)

        return response
