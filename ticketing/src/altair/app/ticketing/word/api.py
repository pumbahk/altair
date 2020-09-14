# -*- coding:utf-8 -*-
import logging
import urllib2

from altair.app.ticketing.api.impl import BaseCommunicationApi
from altair.app.ticketing.api.interfaces import ICommunicationApi

logger = logging.getLogger(__file__)
from zope.interface import implementer


@implementer(ICommunicationApi)
class CMSWordsApi(BaseCommunicationApi):
    def __init__(self, baseurl, apikey):
        self.baseurl = baseurl
        self.apikey = apikey

    def get_url(self, path):
        return self.baseurl.rstrip("/") + "/" + path.lstrip("/")

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
            logger.warn(
                "*communication api* -- {e} : code={code} url={url} reason={reason}".format(e=e, code=e.code, url=e.url,
                                                                                            reason=e.reason))
            raise
