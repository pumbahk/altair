# encoding: utf-8

import urllib
import logging
from urlparse import urljoin
from lxml import etree
from email.message import Message
from zope.interface import implementer
from .interfaces import IFamiPortEndpoints, IFamiPortCommunicator

logger = logging.getLogger(__name__)

def parse_content_type(header_value):
    m = Message()
    m['Content-Type'] = header_value
    return m.get_content_type(), m.get_charsets()[0]

@implementer(IFamiPortEndpoints)
class Endpoints(object):
    def __init__(self, endpoint_base):
        endpoint_base = endpoint_base.rstrip('/') + '/'
        self.endpoint_base = endpoint_base
        self.inquiry = urljoin(endpoint_base, 'reservation/inquiry')  # 予約照会
        self.payment = urljoin(endpoint_base, 'reservation/payment')  # 入金発券
        self.completion = urljoin(endpoint_base, 'reservation/completion')  # 入金発券完了
        self.cancel = urljoin(endpoint_base, 'reservation/cancel')  # 入金発券取消
        self.information = urljoin(endpoint_base, 'reservation/information')  # 案内通信
        self.customer = urljoin(endpoint_base, 'reservation/customer')  # 顧客情報取得
        self.refund = urljoin(endpoint_base, 'refund')  # 払戻

class CommunicationError(Exception):
    pass

@implementer(IFamiPortCommunicator)
class Communicator(object):
    def __init__(self, endpoints, opener, encoding):
        self.endpoints = endpoints
        self.opener = opener
        self.encoding = encoding

    def _parse_response(self, n):
        if n.tag != 'FMIF':
            raise CommunicationError('outermost tag is not FMIF (got %s)' % n.tag)
        retval = {}
        for cn in n:
            retval[cn.tag] = cn.text
        return retval

    def _do_request(self, endpoint, data):
        try:
            logger.debug('making request to %s with %r' % (endpoint, data))
            resp = self.opener.open(
                endpoint,
                data=urllib.urlencode([
                    (k.encode(self.encoding), unicode(v).encode(self.encoding))
                    for k, v in data.items()
                    ])
                )
            mime_type, charset = parse_content_type(resp.info()['content-type'])
            if mime_type != 'text/xml':
                raise CommunicationError("content_type is not 'text/xml' (got %s)" % mime_type)
            retval = self._parse_response(etree.parse(resp).getroot())
            logger.debug('result=%r' % retval)
            return retval
        except Exception as e:
            raise CommunicationError('error occurred during accessing to %s (data=%r): %s' % (endpoint, data, e))

    def fetch_information(self, type, store_code, client_code, event_code_1, event_code_2, performance_code, sales_segment_code, reserve_number, auth_number):
        data = {
            u'infoKubun': type,
            u'storeCode': store_code,
            u'playGuideId': client_code,
            }
        if event_code_1 is not None:
            if event_code_2 is None or performance_code is None or sales_segment_code is None:
                raise CommunicationError('event_code_1 is not None but event_code_2, performance_code or sales_segment_code is None')
            data[u'kogyoCode'] = event_code_1
            data[u'kogyoSubCode'] = event_code_2
            data[u'koenCode'] = performance_code
            data[u'uketsukeCode'] = sales_segment_code
        if auth_number is not None:
            data[u'authNumber'] = auth_number
        if reserve_number is not None:
            data[u'reserveNumber'] = reserve_number
        return self._do_request(self.endpoints.information, data)

def includeme(config):
    import urllib2
    endpoints = Endpoints(config.registry.settings['altair.famiport.simulator.endpoint_url'])
    opener = urllib2.build_opener()
    communicator = Communicator(endpoints, opener, 'Shift_JIS')
    config.registry.registerUtility(communicator, IFamiPortCommunicator)
