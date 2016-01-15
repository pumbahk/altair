# coding: utf-8

import urllib2
import time
import logging
import six
import socket

from zope.interface import implementer
from .exceptions import SejServerError
from .interfaces import ISejPaymentAPICommunicator, ISejPaymentAPICommunicatorFactory
from .payload import create_request_params, create_sej_request, parse_sej_response
from .models import SejTicketType, SejPaymentType
from altair.app.ticketing.urllib2ext import opener_factory_from_config

logger = logging.getLogger(__name__)

@implementer(ISejPaymentAPICommunicator)
class SejPaymentAPICommunicator(object):

    url = ''
    secret_key = ''

    timeout = None
    retry_count = 3
    retry_interval = 5

    def __init__(self, secret_key, url, shop_id, timeout=None, retry_count=3, retry_interval=5, opener=None):
        assert isinstance(secret_key, basestring)
        assert isinstance(url, basestring)
        assert isinstance(shop_id, basestring)
        self.secret_key = secret_key
        self.url = url
        self.shop_id = shop_id
        if timeout is None:
            timeout = socket._GLOBAL_DEFAULT_TIMEOUT
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_interval = retry_interval
        self.opener = opener or urllib2.build_opener()

    def request_file(self, params, retry_mode=False):
        params['X_shop_id'] = self.shop_id
        request_params = create_request_params(params, self.secret_key)
        status, reason, body = self.send_request(request_params, retry_mode)
        if status != 800:
            raise SejServerError(status_code=status, reason=reason, body=body)
        return body

    def request(self, params, retry_mode=False):
        params['X_shop_id'] = self.shop_id
        request_params = create_request_params(params, self.secret_key)
        status, reason, body = self.send_request(request_params, retry_mode)
        if status == 200:
            # status == 200 はSyntaxErrorなんだって！
            reason="Script syntax error"
        if status not in (800, 902, 910):
            raise SejServerError(status_code=status, reason=reason, body=body)
        return parse_sej_response(body, "SENBDATA")

    def send_request(self, request_params, retry_flg=False):
        count = self.retry_count
        while count >= 0:
            try:
                return self._send_request(request_params, retry_flg)
            except:
                if count == 0:
                    logger.exception("communication failure")
                    raise SejServerError(
                        status_code=0,
                        reason='Sej Server connection error',
                        body=None
                        )
                else:
                    logger.exception('will retry (%d attempts left)...' % count) 
            retry_flg = True
            time.sleep(self.retry_interval)
            count -= 1

    def _send_request(self, request_params, retry_flg):
        if retry_flg:
            request_params['retry_cnt'] = '1'
        req = create_sej_request(self.url, request_params)

        try:
            res = self.opener.open(req, timeout=self.timeout)
        except urllib2.HTTPError as e:
            res = e

        status = res.code
        reason = res.msg
        body = res.read()

        logger.info("[response]\n%s" % body)

        return status, reason, body

@implementer(ISejPaymentAPICommunicatorFactory)
class SejPaymentAPICommunicatorFactory(object):
    OPENER_FACTORY_KEY = 'altair.sej.urllib2_opener_factory'
    DEFAULT_OPENER_FACTORY = 'altair.app.ticketing.urllib2ext.build_opener'
    target = SejPaymentAPICommunicator

    def __init__(self, config):
        registry = config.registry
        settings = registry.settings
        self.default_inticket_api_url = \
            settings.get('altair.sej.inticket_api_url') or \
            settings.get('sej.inticket_api_url') # B/C
        self.default_shop_id = \
            settings.get('altair.sej.shop_id') or \
            settings.get('sej.shop_id') # B/C
        self.default_api_key = \
            settings.get('altair.sej.api_key') or \
            settings.get('sej.api_key') # B/C
        timeout = settings.get('altair.sej.timeout', '20')
        self.timeout = timeout and int(timeout) or None
        retry_count = settings.get('altair.sej.retry_count', '3')
        self.retry_count = retry_count and int(retry_count) or None
        retry_interval = settings.get('altair.sej.retry_interval', '3')
        self.retry_interval = retry_interval and int(retry_interval) or None
        self.opener_factory = opener_factory_from_config(config, self.OPENER_FACTORY_KEY, self.DEFAULT_OPENER_FACTORY)

    def __call__(self, tenant, path):
        inticket_api_url = (tenant and tenant.inticket_api_url) or self.default_inticket_api_url
        shop_id = (tenant and tenant.shop_id) or self.default_shop_id
        api_key = (tenant and tenant.api_key) or self.default_api_key

        return self.target(
            secret_key=api_key,
            url=(inticket_api_url + path),
            shop_id=shop_id,
            timeout=self.timeout,
            retry_count=self.retry_count,
            retry_interval=self.retry_interval,
            opener=self.opener_factory()
            )

def includeme(config):
    factory = SejPaymentAPICommunicatorFactory(config)
    config.registry.registerUtility(factory, ISejPaymentAPICommunicatorFactory)
