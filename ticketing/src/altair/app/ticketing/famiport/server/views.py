# -*- coding: utf-8 -*-
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import (
    view_config,
    view_defaults,
    )
from ..communication import FamiPortRequestType
from ..builders import FamiPortRequestFactory
from ..testing import (
    get_response_builder,
    get_payload_builder,
    )


@view_defaults(renderer='famiport-xml')
class ResevationView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _build_payload(self, params, request_type):
        """responseのpayloadを生成する
        """
        famiport_request = FamiPortRequestFactory.create_request(params, request_type)
        response_builder = get_response_builder(self.request)
        payload_builder = get_payload_builder(self.request)
        famiport_response = response_builder.build_response(famiport_request)
        return payload_builder.build_payload(famiport_response)

    @view_config(route_name='famiport.api.reservation.inquiry', request_method='POST')
    def inquiry(self):
        type_ = FamiPortRequestType.ReservationInquiry
        params = dict(self.request.params)
        try:
            params = {
                'storeCode': self.request.POST['storeCode'],
                'ticketingDate': self.request.POST['ticketingDate'],
                'reserveNumber': self.request.POST['reserveNumber'],
                'authNumber': self.request.POST.get('authNumber', ''),
                }
        except KeyError:
            return HTTPBadRequest()
        buf = self._build_payload(params, type_)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.payment', request_method='POST')
    def payment(self):
        type_ = FamiPortRequestType.PaymentTicketing
        params = dict(self.request.params)
        try:
            params = {
                'storeCode': self.request.POST['storeCode'],
                'mmkNo': self.request.POST['mmkNo'],
                'ticketingDate': self.request.POST['ticketingDate'],
                'sequenceNo': self.request.POST['sequenceNo'],
                'playGuideId': self.request.POST.get('playGuideId', ''),  # optional
                'barCodeNo': self.request.POST['barCodeNo'],
                'customerName': self.request.POST.get('customerName', ''),  # optional
                'phoneNumber': self.request.POST.get('phoneNumber', ''),  # optional
                }
        except KeyError:
            return HTTPBadRequest()
        buf = self._build_payload(params, type_)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.completion', request_method='POST')
    def completion(self):
        type_ = FamiPortRequestType.PaymentTicketingCompletion
        params = dict(self.request.params)
        try:
            params = {
                'storeCode': self.request.POST['storeCode'],
                'mmkNo': self.request.POST['mmkNo'],
                'ticketingDate': self.request.POST['ticketingDate'],
                'sequenceNo': self.request.POST['sequenceNo'],
                'barCodeNo': self.request.POST['barCodeNo'],
                'playGuideId': self.request.POST.get('playGuideId', ''),  # optional
                'orderId': self.request.POST['orderId'],
                'totalAmount': self.request.POST['totalAmount'],
                }
        except KeyError:
            return HTTPBadRequest()
        buf = self._build_payload(params, type_)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.cancel', request_method='POST')
    def cancel(self):
        type_ = FamiPortRequestType.PaymentTicketingCancel
        params = dict(self.request.params)
        try:
            params = {
                'storeCode': self.request.POST['storeCode'],
                'mmkNo': self.request.POST['mmkNo'],
                'ticketingDate': self.request.POST['ticketingDate'],
                'sequenceNo': self.request.POST['sequenceNo'],
                'barCodeNo': self.request.POST['barCodeNo'],
                'playGuideId': self.request.POST.get('playGuideId', ''),  # optional
                'orderId': self.request.POST['orderId'],
                'cancelCode': self.request.POST['cancelCode'],
                }
        except KeyError:
            return HTTPBadRequest()
        buf = self._build_payload(params, type_)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.information', request_method='POST')
    def information(self):
        type_ = FamiPortRequestType.Information
        params = dict(self.request.params)
        try:
            params = {
                'infoKubun': self.request.POST['infoKubun'],
                'storeCode': self.request.POST['storeCode'],
                'kogyoCode': self.request.POST['kogyoCode'],
                'kogyoSubCode': self.request.POST['kogyoSubCode'],
                'koenCode': self.request.POST['koenCode'],
                'uketsukeCode': self.request.POST['uketsukeCode'],
                'playGuideId': self.request.POST.get('playGuideId', ''),  # optional
                'authCode': self.request.POST.get('authCode', ''),  # optional
                'reserveNumber': self.request.POST['reserveNumber'],
                }
        except KeyError as err:
            return HTTPBadRequest(err)
        buf = self._build_payload(params, type_)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.customer', request_method='POST')
    def customer(self):
        type_ = FamiPortRequestType.CustomerInformation
        params = dict(self.request.params)
        try:
            params = {
                'storeCode': self.request.POST['storeCode'],
                'mmkNo': self.request.POST['mmkNo'],
                'ticketingDate': self.request.POST['ticketingDate'],
                'sequenceNo': self.request.POST['sequenceNo'],
                'barCodeNo': self.request.POST['barCodeNo'],
                'playGuideId': self.request.POST.get('playGuideId', ''),  # optional
                'orderId': self.request.POST['orderId'],
                'totalAmount': self.request.POST['totalAmount'],
                }
        except KeyError:
            return HTTPBadRequest()
        buf = self._build_payload(params, type_)
        return Response(buf)
