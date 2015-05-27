# -*- coding: utf-8 -*-
import enum


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8063
DEFAULT_PROTOCOL = 'http'


class FamiPortReserveAPIURL(enum.Enum):
    INQUIRY = '/reservation/inquiry'
    PAYMENT = '/reservation/payment'
    COMPLETION = '/reservation/completion'
    CANCEL = '/reservation/cancel'
    INFORMATION = '/reservation/information'
    CUSTOMER = '/reservation/customer'
