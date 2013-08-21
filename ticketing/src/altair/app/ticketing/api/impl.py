# -*- coding:utf-8 -*-
import urllib2
import base64
from .interfaces import ICommunicationApi
from .interfaces import IAPIRequestCreate

import logging
logger=logging.getLogger(__file__)
from zope.interface import implementer

class BaseCommunicationApi(object):
    def bind_instance(self, config):
        config.registry.registerUtility(self, ICommunicationApi, self.__class__.__name__)

    @classmethod
    def get_instance(cls, request):
        return get_communication_api(request, cls)

@implementer(ICommunicationApi)
class CMSCommunicationApi(BaseCommunicationApi):
    def __init__(self, baseurl, apikey):
        self.baseurl = baseurl
        self.apikey = apikey

    def get_url(self, path):
        return self.baseurl.rstrip("/") +"/" + path.lstrip("/")

    def create_connection(self, path, params=None):
        url = self.get_url(path)
        logger.debug("*api* %s: url=%s" % (self.__class__.__name__, url))

        req = urllib2.Request(url, data=params)

        req.add_header('X-Altair-Authorization', self.apikey)
        req.add_header('Connection', 'close')
        return req

    def create_response(self, path, params=None):
        try:
            req = self.create_connection(path, params)
            return urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            logger.warn("*communication api* -- {e} : code={code} url={url} reason={reason}".format(e=e, code=e.code, url=e.url, reason=e.reason))
            raise

def get_communication_api(request, cls):
    return request.registry.queryUtility(ICommunicationApi, cls.__name__)

def bind_communication_api(config, cls, *args, **kwargs):
    """ init でapiを設定"""
    cls = config.maybe_dotted(cls)
    instance = cls(*args, **kwargs)
    config.registry.registerUtility(instance, ICommunicationApi, cls.__name__)


## request create
class BasicAuthRequestCreate(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __call__(self, url, data=None, headers=None, encoding="utf-8"):
        req = urllib2.Request(url, data, headers)
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)   
        return req

DefaultAPIRequestCreate = lambda : urllib2.Request

