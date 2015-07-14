# encoding: utf-8

import logging
import six
import json
from email.message import Message
from pyramid.config import ConfigurationError
from pyramid.events import subscriber
import urllib2
from .models import FamiPortReceiptType
from .interfaces import IReceiptCompleted, IReceiptCanceled, IOrderCanceled

logger = logging.getLogger(__name__)

def parse_content_type(header_value):
    m = Message()
    m['Content-Type'] = header_value
    return m.get_content_type(), m.get_charsets()[0]

class OrderStatusReflector(object):
    DEFAULT_OPENER_FACTORY = 'altair.app.ticketing.urllib2ext.build_opener'
    OPENER_FACTORY_KEY = 'altair.famiport.order_status_reflector.urllib2_opener_factory'
    ENDPOINT_PREFIX = 'altair.famiport.order_status_reflector.endpoint'

    def __init__(self, config):
        settings = config.registry.settings
        endpoints = {
            'completed': None,
            'canceled': None,
            'refunded': None,
            }

        for k in list(six.iterkeys(endpoints)):
            k_ = '%s.%s' % (self.ENDPOINT_PREFIX, k)
            v = settings.get(k_)
            if v is None:
                raise ConfigurationError('%s is not provided' % k_)
            endpoints[k] = v
        opener_factory_ref = settings.get(self.OPENER_FACTORY_KEY, '').strip()
        opener_factory_args = {}
        if not opener_factory_ref:
            opener_factory_ref = self.DEFAULT_OPENER_FACTORY
            logger.info('%s is not specified; defaulting to %s and opener_factory arguments will be ignored too!' % (self.OPENER_FACTORY_KEY, opener_factory_ref))
        else:
            # opener_factory が明示的に指定されたときのみ opener_factory_args を populate する
            # そうでないと、予期せぬ引数がデフォルトの opener_factory に渡されることになるため
            for k, v in six.iteritems(settings):
                if k.startswith(self.OPENER_FACTORY_KEY):
                    k = k[len(self.OPENER_FACTORY_KEY) + 1:]
                    if k:
                        opener_factory_args[k] = v
        opener_factory = config.maybe_dotted(opener_factory_ref)
        self.new_opener = lambda: opener_factory(**opener_factory_args) 
        self.endpoints = endpoints
        logger.info('endpoints=%r' % endpoints)

    def make_json_request(self, url, data):
        req = urllib2.Request(
            url=url,
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                },
            data=json.dumps(
                data,
                encoding='UTF-8',
                ensure_ascii=False
                )
            )
        opener = self.new_opener()
        resp = opener.open(req)
        mime_type, charset = parse_content_type(resp.info()['content-type'])
        if mime_type != 'application/json':
            raise Exception(u'mime type is not application/json')
        retval = json.load(resp, encoding=charset)
        logger.debug('retval=%r' % retval)
        if retval['status'] == 'ok':
            pass
        elif retval['status'] == 'error':
            raise Exception('API returned error status: %s' % retval.get('message', '(message not provided)'))
        else:
            raise Exception('unknown status: %s' % retval['status'])
        return retval

    def receipt_completed(self, event):
        request = event.request
        famiport_receipt = event.famiport_receipt
        famiport_order = famiport_receipt.famiport_order
        if famiport_receipt.type == FamiPortReceiptType.Payment.value:
            type_ = ['payment']
        elif event.famiport_receipt.type == FamiPortReceiptType.Ticketing.value:
            type_ = ['ticketing']
        elif famiport_receipt.type == FamiPortReceiptType.CashOnDelivery.value:
            type_ = ['payment', 'ticketing']
        try:
            self.make_json_request(
                url=self.endpoints['completed'],
                data={
                    'type': type_,
                    'client_code': famiport_order.client_code,
                    'order_no': famiport_order.order_no,
                    'famiport_order_identifier': famiport_receipt.famiport_order_identifier,
                    'payment_reserve_number': famiport_order.payment_famiport_receipt and famiport_order.payment_famiport_receipt.reserve_number,
                    'ticketing_reserve_number': famiport_order.ticketing_famiport_receipt and famiport_order.ticketing_famiport_receipt.reserve_number,
                    }
                )
        except:
            logger.exception('exception ignored')

    def receipt_canceled(self, event):
        request = event.request
        famiport_receipt = event.famiport_receipt
        famiport_order = famiport_receipt.famiport_order
        if famiport_receipt.type == FamiPortReceiptType.Payment.value:
            type_ = ['payment']
        elif event.famiport_receipt.type == FamiPortReceiptType.Ticketing.value:
            type_ = ['ticketing']
        elif famiport_receipt.type == FamiPortReceiptType.CashOnDelivery.value:
            type_ = ['payment', 'ticketing']
        try:
            self.make_json_request(
                url=self.endpoints['canceled'],
                data={
                    'type': type_,
                    'client_code': famiport_order.client_code,
                    'order_no': famiport_order.order_no,
                    'famiport_order_identifier': famiport_receipt.famiport_order_identifier,
                    'payment_reserve_number': famiport_order.payment_famiport_receipt and famiport_order.payment_famiport_receipt.reserve_number,
                    'ticketing_reserve_number': famiport_order.ticketing_famiport_receipt and famiport_order.ticketing_famiport_receipt.reserve_number,
                    }
                )
        except:
            logger.exception('exception ignored')

    def order_canceled(self, event):
        request = event.request
        famiport_order = event.famiport_order
        try:
            self.make_json_request(
                url=self.endpoints['canceled'],
                data={
                    'type': ['order'],
                    'client_code': famiport_order.client_code,
                    'order_no': famiport_order.order_no,
                    'famiport_order_identifier': u'',
                    'payment_reserve_number': famiport_order.payment_famiport_receipt and famiport_order.payment_famiport_receipt.reserve_number,
                    'ticketing_reserve_number': famiport_order.ticketing_famiport_receipt and famiport_order.ticketing_famiport_receipt.reserve_number,
                    }
                )
        except:
            logger.exception('exception ignored')


def includeme(config):
    reflector = OrderStatusReflector(config)
    config.add_subscriber(
        reflector.receipt_completed,
        IReceiptCompleted,
        )
    config.add_subscriber(
        reflector.receipt_canceled,
        IReceiptCanceled
        )
    config.add_subscriber(
        reflector.order_canceled,
        IOrderCanceled 
        )


