from zope.interface import Interface, Attribute, implements
import oauth.oauth as oauth
from ticketing.models.oauth_data_store import AltairAuthDataStore

REALM = 'http://altair.example.net/'

class OAuth(object):
    def __init__(self, request):
        self.request = request
        self.oauth_server = oauth.OAuthServer(AltairAuthDataStore())
        self.oauth_server.add_signature_method(oauth.OAuthSignatureMethod_PLAINTEXT())
        self.oauth_server.add_signature_method(oauth.OAuthSignatureMethod_HMAC_SHA1())

        postdata = None
        if self.request.method == 'POST':
            postdata = request.body
        print self.request.method
        print request.url
        print 111
        print repr(dict(request.headers.items()))
        print postdata
        self.oauth_request = oauth.OAuthRequest.from_request(self.request.method, request.url, headers=request.headers, query_string=postdata)
        print self.oauth_request

    def send_oauth_error(self, err=None):
        self.send_error(401, str(err.message))
        header = oauth.build_authenticate_header(realm=REALM)
        for k, v in header.iteritems():
            self.send_header(k, v)

class Root(object):
    def __init__(self, request):
        self.request = request

class ActingAsBreadcrumb(Interface):
    navigation_parent = Attribute('')
    navigation_name = Attribute('')

class Titled(Interface):
    title = Attribute('')
