from jsonrpclib import jsonrpc
from ticketing.api.impl import BaseCommunicationApi
from StringIO import StringIO
from ..response import FileLikeResponse

# sej ticket template
from ticketing.payments.payment import get_delivery_plugin
from ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
import urllib2



def as_filelike_response(request, imgdata):
    return FileLikeResponse(StringIO(imgdata), 
                            content_type="image/png", 
                            request=request)

boundary = "--------python"
def multipart_formdata(form_dict, encoding="utf-8", boundary=boundary):
    disposition ='Content-Disposition: form-data; name="%s"'
    
    io = StringIO()
    for k, v in form_dict.iteritems():
        io.write('--' + boundary)
        io.write("\r\n")
        io.write(disposition % k)
        io.write("\r\n")
        io.write('')
        io.write("\r\n")
        io.write(v)
        io.write("\r\n")
    io.write("--" + boundary + "--")
    io.write("\r\n")
    io.write('')
    io.write("\r\n")
    return io.getvalue()

def multipart_request(url, encoding="utf-8", boundary=boundary):
    req = urllib2.Request(url)
    req.add_header("Content-Type", 
                   "multipart/form-data; boundary=%s" % boundary)
    return req
    
class SVGPreviewCommunication(BaseCommunicationApi):
    def __init__(self, post_url):
        self.post_url = post_url

    def communicate(self, request, svg):
        rpc_proxy = jsonrpc.ServerProxy(self.post_url, version="2.0")
        imgdata = rpc_proxy.renderSVG(svg,"image/png")
        return imgdata

class SEJPreviewCommunication(BaseCommunicationApi):
    def __init__(self, post_url):
        self.post_url = post_url
        
    def communicate(self, request, ptct):
        delivery_plugin = get_delivery_plugin(request, SEJ_DELIVERY_PLUGIN_ID)
        params =  dict(template=open(delivery_plugin.template, "rb").read(), 
                       ptct=ptct)
        return urllib2.urlopen( multipart_request(self.post_url), 
                                multipart_formdata(params)).read()
