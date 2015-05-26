# -*- coding: utf-8 -*-
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import (
    view_config,
    view_defaults,
    )

from .models import (
    FamiPortReservationInquiryRequest,
    FamiPortPaymentTicketingRequest,
    FamiPortPaymentTicketingCompletionRequest,
    FamiPortPaymentTicketingCancelRequest,
    FamiPortInformationRequest,
    FamiPortCustomerInformationRequest,
    )
from .fakers import (
    get_response_builder,
    get_payload_builder,
    )


@view_defaults(renderer='famiport-xml')
class ResevationView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _build_payload(self, famiport_request):
        response_builder = get_response_builder(self.request)
        payload_builder = get_payload_builder(self.request)
        famiport_response = response_builder.build_response(famiport_request)
        return payload_builder.build_payload(famiport_response)

    @view_config(route_name='famiport.api.reservation.inquiry', request_method='POST')
    def inquiry(self):
        klass = FamiPortReservationInquiryRequest
        famiport_request = klass()
        famiport_request.storeCode = self.request.POST.get('storeCode', '')
        famiport_request.ticketingDate = self.request.POST.get('ticketingDate', '')
        famiport_request.reserveNumber = self.request.POST.get('reserveNumber', '')
        famiport_request.authNumber = self.request.POST.get('authNumber', '')

        if not (famiport_request.storeCode and
                famiport_request.ticketingDate and
                famiport_request.reserveNumber):
            return HTTPBadRequest()

        buf = self._build_payload(famiport_request)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.payment', request_method='POST')
    def payment(self):
        klass = FamiPortPaymentTicketingRequest
        famiport_request = klass()

        famiport_request.storeCode = self.request.POST.get('storeCode', '')
        famiport_request.mmkNo = self.request.POST.get('mmkNo', '')
        famiport_request.ticketingDate = self.request.POST.get('ticketingDate', '')
        famiport_request.sequenceNo = self.request.POST.get('sequenceNo', '')
        famiport_request.playGuideId = self.request.POST.get('playGuideId', '')
        famiport_request.barCodeNo = self.request.POST.get('barCodeNo', '')
        famiport_request.customerName = self.request.POST.get('customerName', '')
        famiport_request.phoneNumber = self.request.POST.get('phoneNumber', '')

        if not (famiport_request.storeCode and
                famiport_request.mmkNo and
                famiport_request.ticketingDate and
                famiport_request.sequenceNo and
                famiport_request.barCodeNo):
            return HTTPBadRequest()

        buf = self._build_payload(famiport_request)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.completion', request_method='POST')
    def completion(self):
        klass = FamiPortPaymentTicketingCompletionRequest
        famiport_request = klass()
        famiport_request.storeCode = self.request.POST.get('storeCode', '')
        famiport_request.mmkNo = self.request.POST.get('mmkNo', '')
        famiport_request.ticketingDate = self.request.POST.get('ticketingDate', '')
        famiport_request.sequenceNo = self.request.POST.get('sequenceNo', '')
        famiport_request.barCodeNo = self.request.POST.get('barCodeNo', '')
        famiport_request.playGuideId = self.request.POST.get('playGuideId', '')
        famiport_request.orderId = self.request.POST.get('orderId', '')
        famiport_request.totalAmount = self.request.POST.get('totalAmount', '')

        if not (famiport_request.storeCode and
                famiport_request.mmkNo and
                famiport_request.ticketingDate and
                famiport_request.sequenceNo and
                famiport_request.barCodeNo and
                famiport_request.orderId and
                famiport_request.totalAmount):
            return HTTPBadRequest()

        buf = self._build_payload(famiport_request)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.cancel', request_method='POST')
    def cancel(self):
        klass = FamiPortPaymentTicketingCancelRequest
        famiport_request = klass()
        famiport_request.storeCode = self.request.POST.get('storeCode', '')
        famiport_request.mmkNo = self.request.POST.get('mmkNo', '')
        famiport_request.ticketingDate = self.request.POST.get('ticketingDate', '')
        famiport_request.sequenceNo = self.request.POST.get('sequenceNo', '')
        famiport_request.barCodeNo = self.request.POST.get('barCodeNo', '')
        famiport_request.playGuideId = self.request.POST.get('playGuideId', '')
        famiport_request.orderId = self.request.POST.get('orderId', '')
        famiport_request.cancelCode = self.request.POST.get('cancelCode', '')

        if not (famiport_request.storeCode and
                famiport_request.mmkNo and
                famiport_request.ticketingDate and
                famiport_request.sequenceNo and
                famiport_request.barCodeNo and
                famiport_request.orderId and
                famiport_request.cancelCode):
            return HTTPBadRequest()

        buf = self._build_payload(famiport_request)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.information', request_method='POST')
    def information(self):
        klass = FamiPortInformationRequest
        famiport_request = klass()
        famiport_request.infoKubun = self.request.POST.get('infoKubun', '')
        famiport_request.storeCode = self.request.POST.get('storeCode', '')
        famiport_request.kogyoCode = self.request.POST.get('kogyoCode', '')
        famiport_request.kogyoSubCode = self.request.POST.get('kogyoSubCode', '')
        famiport_request.koenCode = self.request.POST.get('koenCode', '')
        famiport_request.uketsukeCode = self.request.POST.get('uketsukeCode', '')
        famiport_request.playGuideId = self.request.POST.get('playGuideId', '')
        famiport_request.authCode = self.request.POST.get('authCode', '')
        famiport_request.reserveNumber = self.request.POST.get('reserveNumber', '')
        if not (famiport_request.infoKubun and
                famiport_request.storeCode):
                # famiport_request.kogyoCode and
                # famiport_request.kogyoSubCode and
                # famiport_request.koenCode and
                # famiport_request.uketsukeCode and
                # famiport_request.playGuideId and
                # famiport_request.reserveNumber):
            return HTTPBadRequest()

        buf = self._build_payload(famiport_request)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.customer', request_method='POST')
    def customer(self):
        klass = FamiPortCustomerInformationRequest
        famiport_request = klass()
        famiport_request.storeCode = self.request.POST.get('storeCode', '')
        famiport_request.mmkNo = self.request.POST.get('mmkNo', '')
        famiport_request.ticketingDate = self.request.POST.get('ticketingDate', '')
        famiport_request.sequenceNo = self.request.POST.get('sequenceNo', '')
        famiport_request.barCodeNo = self.request.POST.get('barCodeNo', '')
        famiport_request.playGuideId = self.request.POST.get('playGuideId', '')
        famiport_request.orderId = self.request.POST.get('orderId', '')
        famiport_request.totalAmount = self.request.POST.get('totalAmount', '')

        if not (famiport_request.storeCode and
                famiport_request.mmkNo and
                famiport_request.ticketingDate and
                famiport_request.sequenceNo and
                famiport_request.barCodeNo and
                famiport_request.playGuideId and
                famiport_request.orderId and
                famiport_request.totalAmount):
            return HTTPBadRequest()

        buf = self._build_payload(famiport_request)
        return Response(buf)
