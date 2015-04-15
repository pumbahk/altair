# -*- coding: utf-8 -*-
"""
"""

from zope.interface import implementer
from .interfaces import IFamiPortResponseBuilderFactory, IFamiPortResponseBuilder
from .utils import FamiPortRequestType

import logging

logger = logging.getLogger(__name__)

"""

"""
@implementer(IFamiPortResponseBuilderFactory)
class FamiPortResponseBuilderFactory(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, famiport_request):
        request_type = famiport_request.request_type()
        if request_type == FamiPortRequestType.ReservationInquiry:
            return  FamiPortReservationInquiryResponseBuilder()
        elif request_type == FamiPortRequestType.PaymentTicketing:
            return FamiPortPaymentTicketingResponseBuilder()
        elif request_type == FamiPortRequestType.PaymentTicketingCompletion:
            return FamiPortPaymentTicketingCompletionResponseBuilder()
        elif request_type == FamiPortRequestType.PaymentTicketingCancel:
            return FamiPortPaymentTicketingCancelResponseBuilder()
        elif request_type == FamiPortRequestType.Information:
            return FamiPortInformationResponseBuilder()
        else:
            pass

"""

"""
@implementer(IFamiPortResponseBuilder)
class FamiPortResponseBuilder(object):
    def __init__(self, *args, **kwargs):
        pass

    def build_response(famiport_request=None):
        pass

class FamiPortReservationInquiryResponseBuilder(FamiPortResponseBuilder):
    def build_response(famiport_request=None):
        pass

class FamiPortPaymentTicketingResponseBuilder(FamiPortResponseBuilder):
    def build_response(famiport_request=None):
        pass

class FamiPortPaymentTicketingCompletionResponseBuilder(FamiPortResponseBuilder):
    def build_response(famiport_request=None):
        pass

class FamiPortPaymentTicketingCancelResponseBuilder(FamiPortResponseBuilder):
    def build_response(famiport_request=None):
        pass

class FamiPortInformationResponseBuilder(FamiPortResponseBuilder):
    def build_response(famiport_request=None):
        pass