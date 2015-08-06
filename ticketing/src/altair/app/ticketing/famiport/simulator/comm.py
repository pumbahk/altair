# encoding: utf-8
import re
import urllib
import logging
from datetime import datetime
from urlparse import urljoin
from lxml import etree
from email.message import Message
from zope.interface import implementer
from .interfaces import IFamiPortEndpoints, IFamiPortCommunicator
from ..communication.interfaces import IFamiPortTicketPreviewAPI
from ..communication.utils import FamiPortCrypt

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

    def _do_refund_request(self, endpoint, data):
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
            if mime_type != 'text/plain':
                # 仕様書がおかしいので変なヘッダが来る可能性がある
                mime_type, charset = parse_content_type(';'.join(re.split(' +', mime_type, 1)))
                if mime_type != 'text/plain':
                    raise CommunicationError("content_type is not 'text/plain' (got %s)" % mime_type)
            encoded = resp.read().decode(charset or self.encoding)
            logger.debug('result=%r' % encoded)
            retval = dict(
                (k, v)
                for k, _, v in (pair.partition(u'=') for pair in re.split(ur'\r\n|\r|\n', encoded))
                )
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
        if result['koenDate'] and result['koenDate'] not in ('888888888888', '999999999999'):
            # 888888888888 -> チケット料金の注意事項(下記参照)を表示する（「2：前払い（後日渡し）の前払い時」または「4:前払いのみ」の場合のみ）
            # 999999999999 -> 期間内有効券と判断して公演日時を表示しない
            result['koenDate'] = datetime.strptime(result['koenDate'], '%Y%m%d%H%M')
        for c in ['replyClass', 'totalAmount', 'ticketPayment', 'systemFee', 'ticketingFee', 'phoneInput', 'nameInput', 'ticketCountTotal', 'ticketCount']:
            if result[c]:
                result[c] = int(result[c])

        if result['resultCode'] == '00' and result['replyCode'] == u'00':
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

        if result['koenDate'] and result['koenDate'] not in ('888888888888', '999999999999'):
            # 888888888888 -> チケット料金の注意事項(下記参照)を表示する（「2：前払い（後日渡し）の前払い時」または「4:前払いのみ」の場合のみ）
            # 999999999999 -> 期間内有効券と判断して公演日時を表示しない
            result['koenDate'] = datetime.strptime(result['koenDate'], '%Y%m%d%H%M')

        for c in ['ticketingStart', 'ticketingEnd']:
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

    def cancel(self, store_code, mmk_no, ticketing_date, sequence_no, client_code, order_id, barcode_no, cancel_code):
        data = {
            u'storeCode': store_code,
            u'mmkNo': mmk_no,
            u'sequenceNo': sequence_no,
            u'ticketingDate': ticketing_date.strftime("%Y%m%d%H%M%S"),
            u'playGuideId': client_code,
            u'orderId': order_id,
            u'barCodeNo': barcode_no,
            u'cancelCode': cancel_code,
            }
        return self._do_request(self.endpoints.cancel, data)

    def _refund(self, store_code, pos_no, text_type, timestamp, barcodes):
        data = {
            u'BusinessFlg': u'3',
            u'TextTyp': text_type,
            u'EntryTyp': u'1',
            u'ShopNo': store_code.zfill(7),
            u'RegisterNo': pos_no.zfill(2),
            u'TimeStamp': timestamp.strftime('%Y%m%d'),
            }
        data.update(
            (u'BarCode%d' % (i + 1), barcode)
            for i, barcode in enumerate(barcodes)
            )
        result = self._do_refund_request(self.endpoints.refund, data)
        per_barcode_data = []
        no_more_data = False
        for i, _ in enumerate(barcodes):
            suffix = u'%d' % (i + 1)
            barcode_no = result.pop('BarCode%s' % suffix, None)
            if barcode_no is None or barcode_no == u'':
                no_more_data = True
            else:
                if no_more_data:
                    raise CommunicationError('invalid payload')
                per_barcode_data.append(
                    dict(
                        barCodeNo=barcode_no,
                        resultCode=result.pop('ResultCode%s' % suffix),
                        mainTitle=result.pop('MainTitle%s' % suffix),
                        perfDay=result.pop('PerfDay%s' % suffix),
                        repayment=result.pop('Repayment%s' % suffix),
                        refundStart=result.pop('RefundStart%s' % suffix),
                        refundEnd=result.pop('RefundEnd%s' % suffix),
                        ticketTyp=result.pop('TicketTyp%s' % suffix),
                        charge=result.pop('Charge%s' % suffix)
                        )
                    )
        retval = dict(
            businessFlg=result['BusinessFlg'],
            textTyp=result['TextTyp'],
            entryTyp=result['EntryTyp'],
            shopNo=result['ShopNo'],
            registerNo=result['RegisterNo'],
            timeStamp=result['TimeStamp'],
            entries=per_barcode_data
            )
        return retval

    def refund_inquiry(self, store_code, pos_no, timestamp, barcodes):
        return self._refund(store_code, pos_no, u'0', timestamp, barcodes)

    def refund_settlement(self, store_code, pos_no, timestamp, barcodes):
        return self._refund(store_code, pos_no, u'2', timestamp, barcodes)

def includeme(config):
    import urllib2
    settings = config.registry.settings
    endpoints = Endpoints(settings['altair.famiport.simulator.endpoint_url'])
    opener = urllib2.build_opener()
    communicator = Communicator(endpoints, opener, 'Shift_JIS')
    config.registry.registerUtility(communicator, IFamiPortCommunicator)
    from ..communication.preview import FamiPortTicketPreviewAPI, CachingFamiPortTicketPreviewAPIAdapterFactory
    ticket_preview_api = FamiPortTicketPreviewAPI(opener, settings['altair.famiport.ticket_preview_api.endpoint_url'])
    ticket_preview_cache_region = settings.get('altair.famiport.ticket_preview_api.cache_region')
    if ticket_preview_cache_region is not None:
        config.include('pyramid_dogpile_cache')
        ticket_preview_api = CachingFamiPortTicketPreviewAPIAdapterFactory(ticket_preview_cache_region)(ticket_preview_api)
    config.registry.registerUtility(ticket_preview_api, IFamiPortTicketPreviewAPI)
