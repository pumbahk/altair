# -*- coding: utf-8 -*-
from .requests import (
    FamiPortReservationInquiryRequest,
    FamiPortPaymentTicketingRequest,
    FamiPortPaymentTicketingCompletionRequest,
    FamiPortPaymentTicketingCancelRequest,
    FamiPortInformationRequest,
    FamiPortCustomerInformationRequest,
    )
from .responses import (
    FamiPortReservationInquiryResponse,
    FamiPortPaymentTicketingResponse,
    FamiPortPaymentTicketingCompletionResponse,
    FamiPortPaymentTicketingCancelResponse,
    FamiPortInformationResponse,
    FamiPortCustomerInformationResponse,
    )
from .tests.fakers import (
    FamiPortReservationInquiryResponseFakeFactory,
    FamiPortPaymentTicketingResponseFakeFactory,
    FamiPortPaymentTicketingCompletionResponseFakeFactory,
    FamiPortPaymentTicketingCancelResponseFakeFactory,
    FamiPortInformationResponseFakeFactory,
    FamiPortCustomerResponseFakeFactory,
    )


request_response = {
    FamiPortReservationInquiryRequest: FamiPortReservationInquiryResponse,
    FamiPortPaymentTicketingRequest: FamiPortPaymentTicketingResponse,
    FamiPortPaymentTicketingCompletionRequest: FamiPortPaymentTicketingCompletionResponse,
    FamiPortPaymentTicketingCancelRequest: FamiPortPaymentTicketingCancelResponse,
    FamiPortInformationRequest: FamiPortInformationResponse,
    FamiPortCustomerInformationRequest: FamiPortCustomerInformationResponse,
    }

response_faker = {
    FamiPortReservationInquiryResponse: FamiPortReservationInquiryResponseFakeFactory,
    FamiPortPaymentTicketingResponse: FamiPortPaymentTicketingResponseFakeFactory,
    FamiPortPaymentTicketingCompletionResponse: FamiPortPaymentTicketingCompletionResponseFakeFactory,
    FamiPortPaymentTicketingCancelResponse: FamiPortPaymentTicketingCancelResponseFakeFactory,
    FamiPortInformationResponse: FamiPortInformationResponseFakeFactory,
    FamiPortCustomerInformationResponse: FamiPortCustomerResponseFakeFactory,
    }


def get_response_builder(*args, **kwds):
    import mock
    builder = mock.Mock()
    builder.build_response = lambda request, *_args, **_kwds: request_response.get(type(request))()
    return builder


def get_payload_builder(*args, **kwds):
    import mock
    builder = mock.Mock()
    builder.build_payload = lambda response, *_args, **_kwds: response_faker.get(type(response)).create(*_args, **_kwds)
    return builder


class DummyBuilderFactory(object):
    def __init__(self, *args, **kwds):
        pass

    def __call__(self, *args, **kwds):
        from unittest import mock
        return mock.Mock()
