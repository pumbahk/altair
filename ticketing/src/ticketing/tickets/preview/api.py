import urllib2
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from jsonrpclib import jsonrpc
from StringIO import StringIO

from ..response import FileLikeResponse
from ticketing.api.impl import BaseCommunicationApi
from ticketing.payments.payment import get_delivery_plugin
from ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID


def as_filelike_response(request, imgdata):
    return FileLikeResponse(StringIO(imgdata), 
                            content_type="image/png", 
                            request=request)

    
class SVGPreviewCommunication(BaseCommunicationApi):
    def __init__(self, post_url):
        self.post_url = post_url

    def communicate(self, request, svg):
        rpc_proxy = jsonrpc.ServerProxy(self.post_url, version="2.0")
        imgdata = rpc_proxy.renderSVG(svg,"image/png")
        return imgdata


def _make_named_io(name, data):
    io = StringIO(data)
    io.name = name
    return io


class SEJPreviewCommunication(BaseCommunicationApi):
    def __init__(self, post_url, create_request):
        self.post_url = post_url
        self.create_request = create_request #see. ticketing.api.impl
        
    def _normalize(self, ptct):
        return ptct

    def communicate(self, request, ptct):
        register_openers()
        delivery_plugin = get_delivery_plugin(request, SEJ_DELIVERY_PLUGIN_ID)
        values = {'template': open(delivery_plugin.template, "rb"), 
                  'ptct': _make_named_io("ptct.xml", self._normalize(ptct))}
        data, headers = multipart_encode(values)
        req = self.create_request(self.post_url, data, headers)
        return urllib2.urlopen(req).read()
