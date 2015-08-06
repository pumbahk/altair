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

    registry = config.registry
    builder_registry = FamiPortResponseBuilderRegistry()
    builder_registry.add(
        FamiPortReservationInquiryRequest,
        FamiPortReservationInquiryResponseBuilder(registry)
        )
    builder_registry.add(
        FamiPortPaymentTicketingRequest,
        FamiPortPaymentTicketingResponseBuilder(registry)
        )
    builder_registry.add(
        FamiPortPaymentTicketingCompletionRequest,
        FamiPortPaymentTicketingCompletionResponseBuilder(registry)
        )
    builder_registry.add(
        FamiPortPaymentTicketingCancelRequest,
        FamiPortPaymentTicketingCancelResponseBuilder(registry)
        )
    builder_registry.add(
        FamiPortInformationRequest,
        FamiPortInformationResponseBuilder(registry)
        )
    builder_registry.add(
        FamiPortCustomerInformationRequest,
        FamiPortCustomerInformationResponseBuilder(registry)
        )
    builder_registry.add(
        FamiPortRefundEntryRequest,
        FamiPortRefundEntryResponseBuilder(registry)
        )
    registry.registerUtility(builder_registry, IFamiPortResponseBuilderRegistry)

