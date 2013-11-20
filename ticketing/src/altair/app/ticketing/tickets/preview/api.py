# -*- coding:utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import urllib2
import socket
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from jsonrpclib import jsonrpc
from StringIO import StringIO

from ..response import FileLikeResponse
from altair.app.ticketing.api.impl import BaseCommunicationApi
from altair.app.ticketing.payments.api import get_delivery_plugin
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
from altair.app.ticketing import urllib2ext
from . import TicketPreviewAPIException
from .fillvalues import template_collect_vars

def as_filelike_response(request, imgdata):
    return FileLikeResponse(StringIO(imgdata), 
                            content_type="image/png", 
                            request=request)
    
class SVGPreviewCommunication(BaseCommunicationApi):
    def __init__(self, post_url):
        self.post_url = post_url

    def communicate(self, request, svg):
        try:
            rpc_proxy = jsonrpc.ServerProxy(self.post_url, version="2.0")
            imgdata = rpc_proxy.renderSVG(svg,"image/png")
            return imgdata
        except jsonrpc.ProtocolError, e:
            logger.exception(e)
            logger.error("*preview.preview.svg access=%s" % self.post_url)
            raise TicketPreviewAPIException(u"通信に失敗しました。設定ファイルを見なおしてください")
        except socket.error, e:
            logger.exception(e)
            logger.error("*preview.preview.svg access=%s" % self.post_url)
            raise TicketPreviewAPIException(u"通信に失敗しました。previewサーバのアクセスURLが異なるかもしれません。設定ファイルを見なおしてください")

def _make_named_io(name, data):
    io = StringIO(data)
    io.name = name
    return io


class SEJPreviewCommunication(BaseCommunicationApi):
    def __init__(self, post_url):
        self.post_url = post_url
        
    def _normalize(self, ptct):
        return ptct

    def communicate(self, request, ptct):
        register_openers()
        delivery_plugin = get_delivery_plugin(request, SEJ_DELIVERY_PLUGIN_ID)
        values = {'template': open(delivery_plugin.template, "rb"), 
                  'ptct': _make_named_io("ptct.xml", self._normalize(ptct))}
        data, headers = multipart_encode(values)
        try:
            return urllib2.urlopen(urllib2ext.BasicAuthSensibleRequest(
                self.post_url,
                data=data,
                headers=headers)
                ).read()
        except Exception, e:
            logger.exception(str(e))
            logger.warn("*sej.preview: data: %s" % values)
            raise TicketPreviewAPIException(u"SEJサーバとの通信に失敗しました")

def get_placeholders_from_ticket(request, ticket):
    return template_collect_vars(ticket.drawing)
