# -*- coding: utf-8 -*-
import enum


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8063
DEFAULT_PROTOCOL = 'http'


class FamiPortReserveAPIURL(enum.Enum):
    INQUIRY = '/famiport/reservation/inquiry'
    PAYMENT = '/famiport/reservation/payment'
    COMPLETION = '/famiport/reservation/completion'
    CANCEL = '/famiport/reservation/cancel'
    INFORMATION = '/famiport/reservation/information'
    CUSTOMER = '/famiport/reservation/customer'
