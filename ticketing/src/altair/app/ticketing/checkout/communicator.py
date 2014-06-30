import httplib
import urllib
import logging
from base64 import b64encode
import urlparse
from lxml import etree

logger = logging.getLogger(__name__)

class AnshinCheckoutCommunicator(object):
    _httplib = httplib

    def __init__(self, api_url, encoding='utf-8'):
        self.api_url = api_url
        self.encoding = encoding

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
            http = self._httplib.HTTPConnection(host=url_parts.hostname, port=url_parts.port)
        elif url_parts.scheme == "https":
            http = self._httplib.HTTPSConnection(host=url_parts.hostname, port=url_parts.port)
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
