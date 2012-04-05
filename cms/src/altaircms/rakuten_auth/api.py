import urllib
import urllib2

from .interfaces import IRakutenOpenID

def get_open_id_consumer(request):
    return request.registry.queryUtility(IRakutenOpenID)

DEFAULT_BASE_URL = 'https://api.id.rakuten.co.jp/openid/auth'

class RakutenOpenID(object):
    def __init__(self, base_url, return_to, consumer_key):
        self.base_url = base_url
        self.return_to = return_to
        self.consumer_key = consumer_key

    def get_redirect_url(self):
        return ("%s?openid.ns=http://specs.openid.net/auth/2.0"
            "&openid.return_to=%s"
            "&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
            "&openid.identity=http://specs.openid.net/auth/2.0/identifier_select"
            "&openid.mode=checkid_setup"
            "&openid.ns.oauth=http://specs.openid.net/extenstions/oauth/1.0"
            "&openid.oauth.consumer=%s"
            "&openid.oauth.scope=rakutenid_basicinfo,rakutenid_contactinfo") % (self.base_url, self.return_to, self.consumer_key)

    def verify_authentication(self, request):
        request_get = request.GET
        ns = request_get['openid.ns']
        op_endpoint = request_get['openid.op_endpoint']
        claimed_id = request_get['openid.claimed_id']
        response_nonce = request_get['openid.response_nonce']
        mode = 'check_authentication'
        identity = request_get['openid.identity']
        return_to = request_get['openid.return_to']
        assoc_handle = request_get['openid.assoc_handle']
        signed = request_get['openid.signed']
        sig = request_get['openid.sig']
        ns_oauth = 'http://specs.openid.net/extenstions/oauth/1.0'
        request_token = request_get['openid.oauth.request_token']
        oauth_scope = 'rakutenid_basicinfo,rakutenid_contactinfo'

        url = ("%s?"
            "openid.ns=%s&openid.op_endpoint=%s"
            "&openid.claimed_id=%s"
            "&openid.response_nonce=%s"
            "&openid.mode=%s"
            "&openid.identity=%s"
            "&openid.return_to=%s"
            "&openid.assoc_handle=%s"
            "&openid.signed=%s"
            "&openid.sig=%s"
            "&openid.ns.oauth=%s"
            "&openid.oauth.request_token=%s"
            "&openid.oauth.scope=%s") % (
           self.base_url, ns, op_endpoint, claimed_id, response_nonce, mode, identity, return_to, assoc_handle,
           signed, sig, ns_oauth, request_token, oauth_scope
        )

        url = self.base_url + "?" + urllib.urlencode(
           [('openid.ns', ns),
            ('openid.op_endpoint', op_endpoint),
            ('openid.claimed_id', claimed_id),
            ('openid.response_nonce',response_nonce),
            ('openid.mode', mode),
            ('openid.identity', identity),
            ('openid.return_to', return_to),
            ('openid.assoc_handle', assoc_handle),
            ('openid.signed', signed),
            ('openid.sig', sig),
            ('openid.ns.oauth', ns_oauth),
            ('openid.oauth.request_token', request_token),
            ('openid.oauth.scope', oauth_scope),
        ])

        f = urllib2.urlopen(url)
        response_body = f.read()
        f.close()

        is_valid = response_body.split("\n")[0].split(":")[1]
        if is_valid == "true":
            return claimed_id
        else:
            return None
