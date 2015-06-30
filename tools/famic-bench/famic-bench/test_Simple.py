# -*- coding: utf-8 -*-
"""Simple FunkLoad test

$Id$
"""
import unittest
from datetime import datetime
import enum
import lxml.etree
from funkload.FunkLoadTestCase import FunkLoadTestCase
from zope.component import (
    createObject,
    getGlobalSiteManager,
)
from zope.component.interfaces import IFactory
from zope.interface import (
    implementer,
    Interface,
    Attribute,
)
from kombu import Connection
import famic.crypto


def element_first(func):
    def _wrap(self, *args, **kwds):
        xpath = func(self, *args, **kwds)
        objs = self._tree.xpath(xpath)
        return objs[0] if len(objs) else None
    return _wrap


class ResponseContext(object):
    def __init__(self, tree):
        self._tree = tree


class InquiryResponseContext(ResponseContext):
    @property
    @element_first
    def result_code(self):
        return '//resultCode/text()'

    @property
    @element_first
    def barcode_no(self):
        return '//barCodeNo/text()'


class PaymentResponseContext(ResponseContext):
    @property
    @element_first
    def result_code(self):
        return '//resultCode/text()'

    @property
    @element_first
    def barcode_no(self):
        return '//barCodeNo/text()'

    @property
    @element_first
    def order_id(self):
        return '//orderId/text()'

    @property
    @element_first
    def total_amount(self):
        return '//totalAmount/text()'


class CompletionResponseContext(ResponseContext):
    @property
    @element_first
    def result_code(self):
        return '//resultCode/text()'

    @property
    @element_first
    def barcode_no(self):
        return '//barCodeNo/text()'

    @property
    @element_first
    def total_amount(self):
        return '//totalAmount/text()'


class CustomerResponseContext(ResponseContext):
    @property
    @element_first
    def result_code(self):
        return '//resultCode/text()'

    @property
    @element_first
    def reply_code(self):
        return '//replyCode/text()'

    @property
    @element_first
    def barcode_no(self):
        return '//barCodeNo/text()'


@implementer(IFactory)
class ResponseContextFactory(object):
    def __init__(self, context_class):
        self.context_class = context_class

    def __call__(self, res):
        tree = lxml.etree.fromstring(res.body)
        return self.context_class(tree)


@enum.unique
class FamiPortAPIURL(enum.Enum):
    inquiry = 'http://localhost:8063/famiport/reservation/inquiry'
    payment = 'http://localhost:8063/famiport/reservation/payment'
    completion = 'http://localhost:8063/famiport/reservation/completion'
    customer = 'http://localhost:8063/famiport/reservation/customer'


class Simple(FunkLoadTestCase):
    """This test use a configuration file Simple.conf."""

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')
        # self.stamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.stamp = '20150625000000'

    def test_it(self):
        reserve_number = self.get_reserve_number()
        inquiry_context = self.inquiry(reserve_number)
        payment_context = self.payment(inquiry_context)
        completion_context = self.completion(payment_context)
        customer_context = self.customer(completion_context)  # noqa

    def get_reserve_number(self):
        '575L2R12LH464'
        que = createObject('receipt_queue')
        msg = que.get(block=True)
        msg.ack()
        return msg.body

    def inquiry(self, reserve_number):
        url = FamiPortAPIURL.inquiry.value
        res = self.post(url, description='inquiry', params=(
            ('reserveNumber', reserve_number),
            ('authNumber', ''),
            ('ticketingDate', self.stamp),
            ('storeCode', '000000'),
        ))
        context = createObject('inquiry', res)
        self.assertIsNotNone(context.barcode_no)
        self.assertEqual(context.result_code, '00')
        return context

    def payment(self, inquiry_context):
        """
        ticketingDate=20150331172554&
        playGuideId=&
        phoneNumber=rfanmRgUZFRRephCwOsgbg%3d%3d&
        customerName=pT6fj7ULQklIfOWBKGyQ6g%3d%3d&
        mmkNo=01&
        barCodeNo=1000000000000&
        sequenceNo=15033100002&
        storeCode=000009&
        """
        barcode_no = inquiry_context.barcode_no
        customer_name = u'test'
        phone_number = u'07011112222'
        crypto = famic.crypto.KusoCrypto(barcode_no.encode())
        ciphertext_customer_name = crypto.encrypt(customer_name.encode())
        ciphertext_phone_number = crypto.encrypt(phone_number.encode())
        print(crypto.decrypt(ciphertext_customer_name))

        res = self.post(
            FamiPortAPIURL.payment.value,
            description='payment',
            params={
                'ticketingDate': self.stamp,
                'playGuideId': '',
                'phoneNumber': ciphertext_phone_number,
                'customerName': ciphertext_customer_name,
                'mmkNo': '1',
                'barCodeNo': barcode_no,
                'sequenceNo': '15033100002',
                'storeCode': '000000',
            })
        context = createObject('payment', res)
        self.assertEqual(context.result_code, '00')
        return context

    def completion(self, payment_context):
        """
        ticketingDate=20150331184114&
        orderId=123456789012&
        totalAmount=1000&
        playGuideId=&
        mmkNo=01&
        barCodeNo=1000000000000&
        sequenceNo=15033100010&
        storeCode=000009&
        """
        res = self.post(
            FamiPortAPIURL.completion.value,
            description='payment',
            params={
                'ticketingDate': self.stamp,
                'orderId': payment_context.order_id,
                'totalAmount': payment_context.total_amount,
                'playGuideId': '',
                'mmkNo': '1',
                'barCodeNo': payment_context.barcode_no,
                'sequenceNo': '',
                'storeCode': '',
            })
        context = createObject('completion', res)
        return context

    def customer(self, completion_context):
        """
        ticketingDate=20150331182222&
        orderId=410900000005&
        totalAmount=2200&
        playGuideId=&
        mmkNo=01&
        barCodeNo=4119000000005&
        sequenceNo=15033100004&
        storeCode=000009&
        """
        res = self.post(
            FamiPortAPIURL.customer.value,
            description='customer',
            params={
                'ticketingDate': self.stamp,
                'orderId': '',
                'totalAmount': completion_context.total_amount,
                'playGuideId': '',
                'mmkNo': '1',
                'barCodeNo': completion_context.barcode_no,
                'sequenceNo': '15033100002',
                'storeCode': '000000',
            })
        context = createObject('customer', res)
        self.assertEqual(context.result_code, '00')
        self.assertEqual(context.reply_code, '00')

    def _test_simple(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        # begin of test ---------------------------------------------
        nb_time = self.conf_getInt('test_simple', 'nb_time')
        for i in range(nb_time):
            self.get(server_url, description='Get url')
        # end of test -----------------------------------------------


def init_db():
    import os
    os.system("""echo "UPDATE FamiPortReceipt """
              """set inquired_at=NULL, payment_request_received_at=NULL, """
              """customer_request_received_at=NULL, completed_at=NULL, """
              """void_at=NULL, rescued_at=NULL;" | """
              """mysql -u root -D famiport""")  # initialize


@implementer(IFactory)
class AMQPConnectionFactory(object):
    def __init__(self, uri):
        self._uri = uri
        self._core = None

    def __call__(self):
        if not self._core:
            self._core = Connection(self._uri)
        return self._core


@implementer(IFactory)
class RecepitQueueFactory(object):
    def __init__(self, name):
        self._name = name
        self._core = None

    def __call__(self):
        if not self._core:
            conn = createObject('amqp')
            self._core = conn.SimpleQueue(self._name)
        return self._core


def setup():
    init_db()
    gsm = getGlobalSiteManager()
    context_name_class = {
        'inquiry': InquiryResponseContext,
        'payment': PaymentResponseContext,
        'completion': CompletionResponseContext,
        'customer': CustomerResponseContext,
    }

    for name, context_class in context_name_class.items():
        factory = ResponseContextFactory(context_class)
        gsm.registerUtility(factory, IFactory, name)

    factory = AMQPConnectionFactory('amqp://guest:guest@localhost:5672//')
    gsm.registerUtility(factory, IFactory, 'amqp')

    factory = RecepitQueueFactory('receipt_queue')
    gsm.registerUtility(factory, IFactory, 'receipt_queue')

setup()


if __name__ in ('main', '__main__'):
    unittest.main()
