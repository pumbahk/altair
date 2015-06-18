# encoding: utf-8

import urllib
import logging
from datetime import datetime
from urlparse import urljoin
from urllib2 import urlopen, Request
from base64 import b64decode
from lxml import etree, builder
from email.message import Message
from zope.interface import implementer
from .interfaces import IFamiPortEndpoints, IFamiPortCommunicator, IFamiPortTicketPreviewAPI
from ..communication.utils import FamiPortCrypt
from .exceptions import FDCAPIError

logger = logging.getLogger(__name__)

def parse_content_type(header_value):
    m = Message()
    m['Content-Type'] = header_value
    return m.get_content_type(), m.get_charsets()[0]

def parse_response(n):
    if n.tag != 'FMIF':
        raise CommunicationError('outermost tag is not FMIF (got %s)' % n.tag)
    def _(d, n):
        for cn in n:
            ev = d.get(cn.tag)
            if len(cn) == 0:
               v = cn.text
            else:
                v = {}
                _(v, cn)
            if ev is not None:
                if not isinstance(ev, list):
                    d[cn.tag] = [ev, v]
                else:
                    d[cn.tag].append(v)
            else:
                d[cn.tag] = v

    retval = {}
    _(retval, n)
    return retval

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
            retval = parse_response(etree.parse(resp).getroot())
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

    def inquiry(self, store_code, ticketing_date, reserve_number, auth_number):
        data = {
            u'storeCode': store_code,
            u'ticketingDate': ticketing_date.strftime("%Y%m%d%H%M%S"),
            u'reserveNumber': reserve_number,
            u'authNumber': auth_number,
            }
        result = self._do_request(self.endpoints.inquiry, data)
        if result['koenDate']:
            result['koenDate'] = datetime.strptime(result['koenDate'], '%Y%m%d%H%M')
        for c in ['replyClass', 'totalAmount', 'ticketPayment', 'systemFee', 'ticketingFee', 'phoneInput', 'nameInput', 'ticketCountTotal', 'ticketCount']:
            if result[c]:
                result[c] = int(result[c])

        if result['resultCode'] == '00':
            cd = FamiPortCrypt(result['barCodeNo'])
            for c in ['name']:
                result[c] = cd.decrypt(result[c])
        return result

    def payment(self, store_code, mmk_no, ticketing_date, sequence_no, client_code, barcode_no, customer_name, customer_phone_number):
        cd = FamiPortCrypt(barcode_no)
        data = {
            u'storeCode': store_code,
            u'mmkNo': mmk_no,
            u'sequenceNo': sequence_no,
            u'ticketingDate': ticketing_date.strftime("%Y%m%d%H%M%S"),
            u'playGuideId': client_code,
            u'barCodeNo': barcode_no,
            u'customerName': cd.encrypt(customer_name or u''),
            u'phoneNumber': cd.encrypt(customer_phone_number or u''),
            }
        result = self._do_request(self.endpoints.payment, data)
        for c in ['koenDate', 'ticketingStart', 'ticketingEnd']:
            if result[c]:
                result[c] = datetime.strptime(result[c], '%Y%m%d%H%M')
        for c in ['replyClass', 'totalAmount', 'ticketPayment', 'systemFee', 'ticketingFee', 'ticketCountTotal', 'ticketCount']:
            if result[c]:
                result[c] = int(result[c])
        return result
    
    def complete(self, store_code, mmk_no, ticketing_date, sequence_no, client_code, order_id, barcode_no, total_amount):
        data = {
            u'storeCode': store_code,
            u'mmkNo': mmk_no,
            u'sequenceNo': sequence_no,
            u'ticketingDate': ticketing_date.strftime("%Y%m%d%H%M%S"),
            u'playGuideId': client_code,
            u'orderId': order_id,
            u'barCodeNo': barcode_no,
            u'totalAmount': total_amount,
            }
        return self._do_request(self.endpoints.completion, data)
    
    def _refund(self, store_code, pos_no, text_type, timestamp, barcodes):
        data = {
            u'businessFlg': u'3',
            u'textTyp': text_type,
            u'entryTyp': u'1',
            u'shopNo': store_code.zfill(7),
            u'registerNo': pos_no.zfill(2),
            u'timeStamp': timestamp.strftime('%Y%m%d'),
            }
        data.update(
            (u'barCode%d' % (i + 1), barcode)
            for i, barcode in enumerate(barcodes)
            )
        retval = self._do_request(self.endpoints.refund, data)
        per_barcode_data = []
        for i, _ in enumerate(barcodes):
            suffix = u'%d' % (i + 1)
            per_barcode_data.append(
                dict(
                    barCodeNo=retval.pop('barCode%s' % suffix),
                    resultCode=retval.pop('resultCode%s' % suffix),
                    mainTitle=retval.pop('mainTitle%s' % suffix),
                    perfDay=retval.pop('perfDay%s' % suffix),
                    repayment=retval.pop('repayment%s' % suffix),
                    refundStart=retval.pop('refundStart%s' % suffix),
                    refundEnd=retval.pop('refundEnd%s' % suffix),
                    ticketTyp=retval.pop('ticketTyp%s' % suffix),
                    charge=retval.pop('charge%s' % suffix)
                    )
                )
        retval['entries'] = per_barcode_data
        return retval

    def refund_inquiry(self, store_code, pos_no, timestamp, barcodes):
        return self._refund(store_code, pos_no, u'0', timestamp, barcodes)

    def refund_settlement(self, store_code, pos_no, timestamp, barcodes):
        return self._refund(store_code, pos_no, u'2', timestamp, barcodes)

@implementer(IFamiPortTicketPreviewAPI)
class FamiPortTicketPreviewAPI(object):
    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url

    def __call__(self, request, discrimination_code, client_code, order_id, barcode_no, name, member_id, address_1, address_2, identify_no, tickets, response_image_type):
        if response_image_type == 'pdf':
            response_image_type = u'1'
        elif response_image_type == 'jpeg':
            response_image_type = u'2'
        c = FamiPortCrypt(order_id)
        E = builder.E
        request_body = '<?xml version="1.0" encoding="Shift_JIS" ?>' + \
            etree.tostring(
                E.FMIF(
                    E.playGuideCode(discrimination_code.zfill(2)),
                    E.clientId(client_code.zfill(24)),
                    E.barCodeNo(barcode_no),
                    E.name(c.encrypt(name)),
                    E.memberId(c.encrypt(member_id)),
                    E.address1(c.encrypt(address_1)),
                    E.address2(c.encrypt(address_2)),
                    E.identifyNo(identify_no),
                    E.responseImageType(response_image_type),
                    *(
                        E.ticket(
                            E.barCodeNo(ticket['barcode_no']),
                            E.templateCode(ticket['template_code']),
                            E.ticketData(ticket['data'])
                            )
                        for ticket in tickets
                        )
                    ),
                encoding='unicode'
                ).encode('CP932')
        logger.info('sending request to %s' % self.endpoint_url)
        request = Request(self.endpoint_url, request_body, headers={'Content-Type': 'text/xml; charset=Shift_JIS'})
        response = urlopen(request)
        xml = etree.parse(response)
        result_code_node = xml.find('resultCode')
        if result_code_node is None:
            raise FDCAPIError('invalid response')
        if result_code_node.text != u'00':
            raise FDCAPIError('server returned error status (%s)' % result_code_node.text)
        return [
            b64decode(encoded_ticket_preview_pictures.text)
            for encoded_ticket_preview_pictures in xml.findall('kenmenImage')
            ]


def includeme(config):
    import urllib2
    settings = config.registry.settings
    endpoints = Endpoints(settings['altair.famiport.simulator.endpoint_url'])
    opener = urllib2.build_opener()
    communicator = Communicator(endpoints, opener, 'Shift_JIS')
    config.registry.registerUtility(communicator, IFamiPortCommunicator)
    ticket_preview_api = FamiPortTicketPreviewAPI(settings['altair.famiport.ticket_preview_api.endpoint_url'])
    config.registry.registerUtility(ticket_preview_api, IFamiPortTicketPreviewAPI)
