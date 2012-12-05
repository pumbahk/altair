from jsonrpclib import jsonrpc
from ticketing.api.impl import BaseCommunicationApi
import base64
from StringIO import StringIO
from .response import FileLikeResponse

class SVGPreviewCommunication(BaseCommunicationApi):
    def __init__(self, post_url, fetch_url):
        self.post_url = post_url
        self.fetch_url = fetch_url

    def communicate(self, request, svg):
        rpc_proxy = jsonrpc.ServerProxy(self.post_url, version="2.0")
        preview_url = rpc_proxy.renderSVG(svg, self.fetch_url)
        return preview_url

    def as_filelike_response(self, request, imgdata):
        return FileLikeResponse(StringIO(base64.b64decode(imgdata)), 
                                content_type="image/png", 
                                request=request)
