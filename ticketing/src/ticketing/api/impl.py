# -*- coding:utf-8 -*-
import urllib2
from .interfaces import ICommunicationApi

from zope.interface import implementer

@implementer(ICommunicationApi)
class CMSCommunicationApi(object):
    def __init__(self, baseurl, apikey):
        self.baseurl = baseurl
        self.apikey = apikey

    def create_connection(self, path, params=None):
        url = self.baseurl.rstrip("/") +"/" + path.lstrip("/")
        req = urllib2.Request(url, data=params)

        req.add_header('X-Altair-Authorization', self.apikey)
        req.add_header('Connection', 'close')
        return req

def get_communication_api(request, cls):
    return request.registry.queryUtility(ICommunicationApi, cls.__name__)

def bound_communication_api(config, cls, *args, **kwargs):
    """ init でapiを設定"""
    cls = config.maybe_dotted(cls)
    instance = cls(*args, **kwargs)
    config.registry.registerUtility(instance, ICommunicationApi, cls.__name__)
