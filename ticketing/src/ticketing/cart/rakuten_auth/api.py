import urllib
import urllib2
import pickle
import urlparse

import oauth2 as oauth
from pyramid import security
from ticketing.cart import logger

from .interfaces import IRakutenOpenID

def authenticated_user(request):
    data = security.authenticated_userid(request)
    if data is None:
        return None
    
    return pickle.loads(data.decode('base64'))

def remember_user(request, user_data):
    data = pickle.dumps(user_data)
            
    headers = security.remember(request, data.encode('base64'))
    return headers

def get_open_id_consumer(request):
    return request.registry.queryUtility(IRakutenOpenID)

DEFAULT_BASE_URL = 'https://api.id.rakuten.co.jp/openid/auth'

class RakutenOpenID(object):
    def __init__(self, base_url, return_to, consumer_key, secret=None, extra_verify_urls=None):
        self.base_url = base_url
        self.return_to = return_to
        self.consumer_key = consumer_key
        self.secret = secret
        if extra_verify_urls is None:
            self.extra_verify_urls = []
        else:
            self.extra_verify_urls = extra_verify_urls



    def get_redirect_url(self):
        return (self.base_url + "?openid.ns=http://specs.openid.net/auth/2.0"
                "&openid.return_to=%(return_to)s"
                "&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
                "&openid.identity=http://specs.openid.net/auth/2.0/identifier_select"
                "&openid.mode=checkid_setup"
                "&openid.ns.oauth=http://specs.openid.net/extenstions/oauth/1.0"
                "&openid.oauth.consumer=%(consumer_key)s"
                "&openid.oauth.scope=rakutenid_basicinfo,rakutenid_contactinfo"
                "&openid.ns.ax=http://openid.net/srv/ax/1.0"
                "&openid.ax.mode=fetch_request"
                "&openid.ax.type.nickname=http://schema.openid.net/namePerson/friendly"
                "&openid.ax.required=nickname"
                ) % dict(return_to=self.return_to, consumer_key=self.consumer_key)

    def openid_params(self, request):
        request_get = request.GET
        return dict(ns = request_get['openid.ns'],
                    op_endpoint = request_get['openid.op_endpoint'],
                    claimed_id = request_get['openid.claimed_id'],
                    response_nonce = request_get['openid.response_nonce'],
                    mode = 'check_authentication',
                    identity = request_get['openid.identity'],
                    return_to = request_get['openid.return_to'],
                    assoc_handle = request_get['openid.assoc_handle'],
                    signed = request_get['openid.signed'],
                    sig = request_get['openid.sig'],
                    ns_oauth = 'http://specs.openid.net/extenstions/oauth/1.0',
                    oauth_request_token = request_get['openid.oauth.request_token'],
                    oauth_scope = 'rakutenid_basicinfo,rakutenid_contactinfo',
                    ns_ax = request_get['openid.ns.ax'],
                    ax_mode = request_get['openid.ax.mode'],
                    ax_type_nickname = request_get['openid.ax.type.nickname'],
                    ax_value_nickname = request_get['openid.ax.value.nickname'],
                    )

    def verify_authentication(self, request, identity):

        url = self.base_url + "?" + urllib.urlencode(
           [('openid.ns', identity['ns']),
            ('openid.op_endpoint', identity['op_endpoint']),
            ('openid.claimed_id', identity['claimed_id']),
            ('openid.response_nonce',identity['response_nonce']),
            ('openid.mode', identity['mode']),
            ('openid.identity', identity['identity']),
            ('openid.return_to', identity['return_to']),
            ('openid.assoc_handle', identity['assoc_handle']),
            ('openid.signed', identity['signed']),
            ('openid.sig', identity['sig']),
            ('openid.ns.oauth', identity['ns_oauth']),
            ('openid.oauth.request_token', identity['oauth_request_token']),
            ('openid.oauth.scope', identity['oauth_scope']),
            ('openid.ns.ax', identity['ns_ax']),
            ('openid.ax.mode', identity['ax_mode']),
            ('openid.ax.type.nickname', identity['ax_type_nickname']),
            ('openid.ax.value.nickname', identity['ax_value_nickname']),
        ])

        f = urllib2.urlopen(url)
        response_body = f.read()
        f.close()

        is_valid = response_body.split("\n")[0].split(":")[1]
        #oauth_consumer = oauth.Consumer(self.consumer_key, self.secret)
        #client = oauth.Client(oauth_consumer, oauth.Token(request_token, self.secret))
        #res, content = client.request('https://api.id.rakuten.co.jp/openid/oauth/accesstoken', 'GET')
        #print content
        #request_token = urlparse.parse_qsl(content)
        #print request_token

        if is_valid == "true":
            return {'clamed_id': identity['claimed_id'], "nickname": identity['ax_value_nickname']}
        else:
            return None
