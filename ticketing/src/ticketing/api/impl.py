# -*- coding:utf-8 -*-
import urllib2
from .interfaces import ICommunicationApi

from zope.interface import implementer

@implementer(ICommunicationApi)
class CMSCommunicationApi(object):
    def __init__(self, baseurl, apikey):
        self.baseurl = baseurl
        self.apikey = apikey

    def create_connection(self, path, params):
        url = self.baseurl.rstrip("/") +"/" + path.lstrip("/")
        req = urllib2.Request(url, params)

        req.add_header('X-Altair-Authorization', self.apikey)
        req.add_header('Connection', 'close')
        return req

def get_cmsapi_conection(request, path, params):
    """ cmsのapiを利用 (汎用化されてない) """
    instance = request.registry.queryUtility(ICommunicationApi, CMSCommunicationApi.__name__)
    if instance:
        return instance.create_connection(path, params)
    return None

def bound_communication_api(config, cls, *args, **kwargs):
    """ init でapiを設定"""
    cls = config.maybe_dotted(cls)
    instance = cls(*args, **kwargs)
    config.registry.registerUtility(instance, ICommunicationApi, cls.__name__)
