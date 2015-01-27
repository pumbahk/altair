import httplib
import urllib
import logging
import ssl
import urlparse
from base64 import b64encode
from lxml import etree
from zope.interface import implementer
from altair.httphelpers.httplib import OurHTTPSConnection
from .interfaces import IAnshinCheckoutCommunicator

logger = logging.getLogger(__name__)

@implementer(IAnshinCheckoutCommunicator)
class AnshinCheckoutCommunicator(object):
    HTTPConnection = httplib.HTTPConnection
    HTTPSConnection = OurHTTPSConnection

    def __init__(self, api_url, encoding='utf-8', ssl_version=ssl.PROTOCOL_SSLv23):
        self.api_url = api_url
        self.encoding = encoding
        self.ssl_version = ssl_version

    @property
    def fixation_order_url(self):
        return self.api_url + '/odrctla/fixationorder/1.0/'

    @property
    def change_order_url(self):
        return self.api_url + '/odrctla/changepayment/1.0/'

    @property
    def cancel_order_url(self):
        return self.api_url + '/odrctla/cancelorder/1.0/'

    def _send_request(self, url, body=None):
        content_type = "application/x-www-form-urlencoded; charset=%s" % self.encoding
        if body is None:
            body = u''
        url_parts = urlparse.urlparse(url)

        if url_parts.scheme == "http":
            http = HTTPConnection(host=url_parts.hostname, port=url_parts.port)
        elif url_parts.scheme == "https":
            http = OurHTTPSConnection(host=url_parts.hostname, port=url_parts.port, ssl_version=self.ssl_version)
        else:
            raise ValueError, "unknown scheme %s" % (url_parts.scheme)

        logger.debug("request %s body = %s" % (url, body))
        headers = {"Content-Type": content_type}
        http.request("POST", url_parts.path, body=body, headers=headers)
        res = http.getresponse()
        try:
            logger.debug('%(url)s %(status)s %(reason)s' % dict(
                url=url,
                status=res.status,
                reason=res.reason,
            ))
            if res.status != 200:
                raise Exception, res.reason
            return etree.parse(res).getroot()
        finally:
            res.close()

    def send_order_fixation_request(self, xml):
        message = etree.tostring(xml, xml_declaration=True, encoding=self.encoding)
        logger.debug('message=%s' % message)
        return self._send_request(self.fixation_order_url, 'rparam=%s' % urllib.quote(b64encode(message)))

    def send_order_change_request(self, xml):
        message = etree.tostring(xml, xml_declaration=True, encoding=self.encoding)
        logger.debug('message=%s' % message)
        return self._send_request(self.change_order_url, 'rparam=%s' % urllib.quote(b64encode(message)))

    def send_order_cancel_request(self, xml):
        message = etree.tostring(xml, xml_declaration=True, encoding=self.encoding)
        logger.debug('message=%s' % message)
        return self._send_request(self.cancel_order_url, 'rparam=%s' % urllib.quote(b64encode(message)))

def resolve_ssl_version(ssl_version):
    if isinstance(ssl_version, basestring):
        return getattr(ssl, 'PROTOCOL_%s' % ssl_version)
    else:
        return ssl_version

def includeme(config):
    settings = config.registry.settings
    api_url = settings.get('altair.anshin_checkout.api_url')
    if api_url is None:
        logger.warning("altair.anshin_checkout.api_url is not given. using deprecated altair_checkout.api_url instead")
        api_url = settings.get('altair_checkout.api_url')
    ssl_version = settings.get('altair.anshin_checkout.ssl_version')
    if ssl_version is None:
        ssl_version = settings.get('altair_checkout.ssl_version')
        if ssl_version is None:
            logger.warning("neither altair.anshin_checkout.ssl_version nor altair_checkout.ssl_version is given. falling back to SSLv23")
            ssl_version = ssl.PROTOCOL_SSLv23
    ssl_version = resolve_ssl_version(ssl_version)
    config.registry.registerUtility(
        AnshinCheckoutCommunicator(
            api_url=api_url,
            ssl_version=ssl_version
            ),
        IAnshinCheckoutCommunicator
        )
