import urllib2
import json
from urlparse import urljoin
from zope.interface import implementer
from .interfaces import ICommunicator
from .exceptions import CommunicationError
from altair.app.ticketing.utils import parse_content_type

@implementer(ICommunicator)
class EaglesCommunicator(object):
    def __init__(self, endpoint_base, opener_factory, request_charset='utf-8'):
        self.endpoint_base = endpoint_base
        self.opener_factory = opener_factory
        self.request_charset = request_charset

    def _do_request(self, endpoint, data):
        req = urllib2.Request(endpoint)
        req.add_header('Content-Type', 'application/json; charset=%s' % self.request_charset)
        req.add_header('Connection', 'close')
        req.add_data(
            json.dumps(
                data,
                ensure_ascii=False,
                ).encode(self.request_charset)
            )
        opener = self.opener_factory()
        try:
            resp = opener.open(req)
        except urllib2.HTTPError as e:
            mime_type, charset = parse_content_type(resp.info()['content-type'])
            if mime_type == 'application/json':
                try:
                    data = json.load(resp, encoding=charset)
                    message = data.pop('message', None)
                    if message is not None:
                        raise CommunicationError(message)
                except:
                    raise e
            raise CommunicationError(e.message)
                
        mime_type, charset = parse_content_type(resp.info()['content-type'])
        if mime_type != 'application/json':
            raise CommunicationError("content_type is not 'application/json' (got %s)" % mime_type)
        return json.load(resp, encoding=charset)

    def get_user_profile(self, openid_claimed_id):
        return self._do_request(
            urljoin(self.endpoint_base, '/user/profile'),
            {u'openid_claimed_id': openid_claimed_id}
            )

def includeme(config):
    from altair.app.ticketing.urllib2ext import opener_factory_from_config
    config.registry.registerUtility(
        EaglesCommunicator(
            endpoint_base=config.registry.settings['altair.eagles_extauth.endpoint_base'],
            opener_factory=opener_factory_from_config(config, 'altair.eagles_extauth.urllib2_opener_factory')
            ),
        ICommunicator
        )
