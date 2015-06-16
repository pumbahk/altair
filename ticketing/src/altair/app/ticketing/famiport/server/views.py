# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import (
    view_config,
    view_defaults,
    )
from pyramid.decorator import reify
from altair.sqlahelper import get_db_session
from ..communication import FamiPortRequestType
from ..communication.builders import FamiPortRequestFactory
from ..communication.api import (
    get_response_builder,
    get_xmlResponse_generator,
    )
from ..communication.models import (
    ResultCodeEnum,
    FamiPortInformationResponse,
    )

_logger = logging.getLogger(__name__)


@view_config(route_name='famiport.api.ping')
def pingpong(request):
    return Response('PONG')


@view_defaults(renderer='famiport-xml')
class ResevationView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @reify
    def session(self):
        return get_db_session(self.request, 'famiport')

    @reify
    def comm_session(self):
        return get_db_session(self.request, 'famiport_comm')

    @reify
    def now(self):
        return datetime.now()

    def _create_famiport_request(self, params, request_type):
        famiport_request = FamiPortRequestFactory.create_request(params, request_type)
        self.comm_session.add(famiport_request)
        self.comm_session.commit()
        return famiport_request

    def _build_response(self, famiport_request):
        """responseのpayloadを生成する
        """
        response_builder = get_response_builder(self.request, famiport_request)
        famiport_response = response_builder.build_response(famiport_request, self.session, self.now)
        self.comm_session.add(famiport_response)
        self.comm_session.commit()
        payload_builder = get_xmlResponse_generator(famiport_response)
        return Response(
            body=payload_builder.generate_xmlResponse(famiport_response),
            content_type='text/xml',
            charset=payload_builder.encoding
            )

    def _create_payload(self, famiport_response):
        payload_builder = get_xmlResponse_generator(famiport_response)
        return payload_builder.generate_xmlResponse(famiport_response)

    @view_config(route_name='famiport.api.reservation.inquiry', request_method='POST')
    def inquiry(self):
        type_ = FamiPortRequestType.ReservationInquiry
        request_params = dict(self.request.params)
        params = {
            'storeCode': request_params.get('storeCode', ''),
            'ticketingDate': request_params.get('ticketingDate', ''),
            'reserveNumber': request_params.get('reserveNumber', ''),
            'authNumber': request_params.get('authNumber', ''),
             }
        famiport_request = self._create_famiport_request(params, type_)
        return self._build_response(famiport_request)

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
        except KeyError as err:
            _logger.error('parameter error: {}'.format(err))
            return HTTPBadRequest()
        famiport_request = self._create_famiport_request(params, type_)
        return self._build_response(famiport_request)

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
        except KeyError as err:
            _logger.error('parameter error: {}'.format(err))
            return HTTPBadRequest()
        famiport_request = self._create_famiport_request(params, type_)
        return self._build_response(famiport_request)

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
        except KeyError as err:
            _logger.error('parameter error: {}'.format(err))
            return HTTPBadRequest()
        famiport_request = self._create_famiport_request(params, type_)
        return self._build_response(famiport_request)

    @view_config(route_name='famiport.api.reservation.information', request_method='POST')
    def information(self):
        type_ = FamiPortRequestType.Information
        request_params = dict(self.request.params)
        params = {
            'infoKubun': request_params.get('infoKubun', ''),
            'storeCode': request_params.get('storeCode', ''),
            'kogyoCode': request_params.get('kogyoCode', ''),   # optional
            'kogyoSubCode': request_params.get('kogyoSubCode', ''),  # optional
            'koenCode': request_params.get('koenCode', ''),  # optional
            'uketsukeCode': request_params.get('uketsukeCode', ''),  # optional
            'playGuideId': request_params.get('playGuideId', ''),  # optional
            'authCode': request_params.get('authCode', ''),  # optional
            'reserveNumber': request_params.get('reserveNumber', ''),  # optional
            }
        famiport_request = self._create_famiport_request(params, type_)
        return self._build_response(famiport_request)

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
        except KeyError as err:
            _logger.error('parameter error: {}'.format(err))
            return HTTPBadRequest(err)
        famiport_request = self._create_famiport_request(params, type_)
        return self._build_response(famiport_request)

    @view_config(route_name='famiport.api.reservation.refund', request_method='POST')
    def refund(self):
        type_ = FamiPortRequestType.RefundEntry
        request_params = dict(self.request.params)
        params = {}
        try:
            params = {
                'businessFlg': request_params['businessFlg'],
                'textTyp': request_params['textTyp'],
                'entryTyp': request_params['entryTyp'],
                'shopNo': request_params['shopNo'],
                'registerNo': request_params['registerNo'],
                }
            for barcode_key in ['barCode1', 'barCode2', 'barCode3', 'barCode4']:
                if barcode_key in request_params:
                    params[barcode_key] = request_params[barcode_key]
        except KeyError as err:
            _logger.error('parameter error: {}'.format(err))
            return HTTPBadRequest()
        famiport_request = self._create_famiport_request(params, type_)
        return self._build_response(famiport_request)
