from jsonrpclib import jsonrpc
from ticketing.api.impl import BaseCommunicationApi
import base64
from StringIO import StringIO
from ..response import FileLikeResponse

class SVGPreviewCommunication(BaseCommunicationApi):
    def __init__(self, post_url):
        self.post_url = post_url

    def communicate(self, request, svg):
        rpc_proxy = jsonrpc.ServerProxy(self.post_url, version="2.0")
        imgdata = rpc_proxy.renderSVG(svg,"image/png")
        return imgdata

    def as_filelike_response64(self, request, imgdata):
        return FileLikeResponse(StringIO(imgdata), 
                                content_type="image/png", 
                                request=request)

    def as_filelike_response(self, request, imgdata):
        return FileLikeResponse(StringIO(base64.b64decode(imgdata)), 
                                content_type="image/png", 
                                request=request)
