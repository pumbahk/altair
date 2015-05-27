# -*- coding: utf-8 -*-
import lxml.etree
from .models import (
    FamiPortReservationInquiryRequest,
    FamiPortPaymentTicketingRequest,
    FamiPortPaymentTicketingCompletionRequest,
    FamiPortPaymentTicketingCancelRequest,
    FamiPortInformationRequest,
    FamiPortCustomerInformationRequest,
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

    def _build_payload_str(response, *args, **kwds):
        typ = type(response)
        fake = response_faker.get(typ)
        assert fake, 'no fake...: {}'.format(typ)
        tree = fake.create(*args, **kwds)
        bstr = lxml.etree.tostring(tree, pretty_print=True)
        return bstr
    builder.build_payload = _build_payload_str
    return builder


class DummyBuilderFactory(object):
    def __init__(self, *args, **kwds):
        pass

    def __call__(self, *args, **kwds):
        from unittest import mock
        return mock.Mock()
