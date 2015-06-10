# -*- coding: utf-8 -*-
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import (
    view_config,
    view_defaults,
    )
from ..communication import FamiPortRequestType
from ..communication.builders import FamiPortRequestFactory
from ..communication.api import (
    get_response_builder,
    get_xmlResponse_generator,
    )


@view_config(route_name='famiport.api.ping')
def pingpong(request):
    return Response('PONG')


@view_defaults(renderer='famiport-xml')
class ResevationView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _build_payload(self, params, request_type):
        """responseのpayloadを生成する
        """
        famiport_request = FamiPortRequestFactory.create_request(params, request_type)
        response_builder = get_response_builder(self.request, famiport_request)
        famiport_response = response_builder.build_response(famiport_request)
        payload_builder = get_xmlResponse_generator(famiport_response)
        return payload_builder.generate_xmlResponse(famiport_response)

    @view_config(route_name='famiport.api.reservation.inquiry', request_method='POST')
    def inquiry(self):
        type_ = FamiPortRequestType.ReservationInquiry
        request_params = dict(self.request.params)
        params = {}
        try:
            params = {
                'storeCode': request_params['storeCode'],
                'ticketingDate': request_params['ticketingDate'],
                'reserveNumber': request_params['reserveNumber'],
                'authNumber': request_params.get('authNumber', ''),
                }
        except KeyError as err:
            return HTTPBadRequest(err)
        buf = self._build_payload(params, type_)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.payment', request_method='POST')
    def payment(self):
        type_ = FamiPortRequestType.PaymentTicketing
        request_params = dict(self.request.params)
        params = {}
        try:
            params = {
                'storeCode': request_params['storeCode'],
                'mmkNo': request_params['mmkNo'],
                'ticketingDate': request_params['ticketingDate'],
                'sequenceNo': request_params['sequenceNo'],
                'playGuideId': request_params.get('playGuideId', ''),  # optional
                'barCodeNo': request_params['barCodeNo'],
                'customerName': request_params.get('customerName', ''),  # optional
                'phoneNumber': request_params.get('phoneNumber', ''),  # optional
                }
        except KeyError:
            return HTTPBadRequest()
        buf = self._build_payload(params, type_)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.completion', request_method='POST')
    def completion(self):
        type_ = FamiPortRequestType.PaymentTicketingCompletion
        request_params = dict(self.request.params)
        params = {}
        try:
            params = {
                'storeCode': request_params['storeCode'],
                'mmkNo': request_params['mmkNo'],
                'ticketingDate': request_params['ticketingDate'],
                'sequenceNo': request_params['sequenceNo'],
                'barCodeNo': request_params['barCodeNo'],
                'playGuideId': request_params.get('playGuideId', ''),  # optional
                'orderId': request_params['orderId'],
                'totalAmount': request_params['totalAmount'],
                }
        except KeyError:
            return HTTPBadRequest()
        buf = self._build_payload(params, type_)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.cancel', request_method='POST')
    def cancel(self):
        type_ = FamiPortRequestType.PaymentTicketingCancel
        request_params = dict(self.request.params)
        params = {}
        try:
            params = {
                'storeCode': request_params['storeCode'],
                'mmkNo': request_params['mmkNo'],
                'ticketingDate': request_params['ticketingDate'],
                'sequenceNo': request_params['sequenceNo'],
                'barCodeNo': request_params['barCodeNo'],
                'playGuideId': request_params.get('playGuideId', ''),  # optional
                'orderId': request_params['orderId'],
                'cancelCode': request_params['cancelCode'],
                }
        except KeyError:
            return HTTPBadRequest()
        buf = self._build_payload(params, type_)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.information', request_method='POST')
    def information(self):
        type_ = FamiPortRequestType.Information
        request_params = dict(self.request.params)
        params = {}
        try:
            params = {
                'infoKubun': request_params['infoKubun'],
                'storeCode': request_params['storeCode'],
                'kogyoCode': request_params['kogyoCode'],
                'kogyoSubCode': request_params['kogyoSubCode'],
                'koenCode': request_params['koenCode'],
                'uketsukeCode': request_params['uketsukeCode'],
                'playGuideId': request_params.get('playGuideId', ''),  # optional
                'authCode': request_params.get('authCode', ''),  # optional
                'reserveNumber': request_params['reserveNumber'],
                }
        except KeyError as err:
            return HTTPBadRequest(err)
        buf = self._build_payload(params, type_)
        return Response(buf)

    @view_config(route_name='famiport.api.reservation.customer', request_method='POST')
    def customer(self):
        type_ = FamiPortRequestType.CustomerInformation
        request_params = dict(self.request.params)
        params = {}
        try:
            params = {
                'storeCode': request_params['storeCode'],
                'mmkNo': request_params['mmkNo'],
                'ticketingDate': request_params['ticketingDate'],
                'sequenceNo': request_params['sequenceNo'],
                'barCodeNo': request_params['barCodeNo'],
                'playGuideId': request_params.get('playGuideId', ''),  # optional
                'orderId': request_params['orderId'],
                'totalAmount': request_params['totalAmount'],
                }
        except KeyError:
            return HTTPBadRequest()
        buf = self._build_payload(params, type_)
        return Response(buf)
