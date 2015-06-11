from .models import *

def includeme(config):
    from .builders import (
        FamiPortResponseBuilderRegistry,
        FamiPortReservationInquiryRequest,
        FamiPortReservationInquiryResponseBuilder,
        FamiPortPaymentTicketingRequest,
        FamiPortPaymentTicketingResponseBuilder,
        FamiPortPaymentTicketingCompletionRequest,
        FamiPortPaymentTicketingCompletionResponseBuilder,
        FamiPortPaymentTicketingCancelRequest,
        FamiPortPaymentTicketingCancelResponseBuilder,
        FamiPortInformationRequest,
        FamiPortInformationResponseBuilder,
        FamiPortCustomerInformationRequest,
        FamiPortCustomerInformationResponseBuilder,
        FamiPortRefundEntryRequest,
        FamiPortRefundEntryResponseBuilder,
        )
    from .interfaces import IFamiPortResponseBuilderRegistry

    builder_registry = FamiPortResponseBuilderRegistry()
    builder_registry.add(
        FamiPortReservationInquiryRequest,
        FamiPortReservationInquiryResponseBuilder()
        )
    builder_registry.add(
        FamiPortPaymentTicketingRequest,
        FamiPortPaymentTicketingResponseBuilder()
        )
    builder_registry.add(
        FamiPortPaymentTicketingCompletionRequest,
        FamiPortPaymentTicketingCompletionResponseBuilder()
        )
    builder_registry.add(
        FamiPortPaymentTicketingCancelRequest,
        FamiPortPaymentTicketingCancelResponseBuilder()
        )
    builder_registry.add(
        FamiPortInformationRequest,
        FamiPortInformationResponseBuilder()
        )
    builder_registry.add(
        FamiPortCustomerInformationRequest,
        FamiPortCustomerInformationResponseBuilder()
        )
    builder_registry.add(
        FamiPortRefundEntryRequest,
        FamiPortRefundEntryResponseBuilder()
        )
    config.registry.registerUtility(builder_registry, IFamiPortResponseBuilderRegistry)

