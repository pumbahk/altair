from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import HTTPClientError

from .helpers import make_sej_response

from .notification.receiver import (
    SejNotificationReceiver,
    SejNotificationSignatureMismatch,
    SejNotificationMissingValue,
    SejNotificationUnknown,
    )

import traceback
import logging

logger = logging.getLogger(__name__)

class SejHTTPErrorResponse(HTTPClientError):
    empty_body = True

    def __init__(self, code, reason, params):
        super(HTTPClientError, self).__init__(code=code, body=make_sej_response(params))

def makeReceiver(request):
    settings = request.registry.settings
    api_key = settings['sej.api_key']
    return SejNotificationReceiver(api_key)

class SejCallback(object):
    def __init__(self, request):
        self.context = request.context
        self.request = request
        from altair.app.ticketing.models import DBSession
        self.session = DBSession

    @view_config(route_name='sej.callback')
    def callback(self):
        logger.info('[callback] %s' % self.request.body)

        try:
            receiver = makeReceiver(self.request)
            sej_notification, retry_data = receiver(self.request.POST)
            self.session.add(sej_notification)
        except SejNotificationSignatureMismatch as e:
            return SejHTTPErrorResponse(
                400, 'Bad Request', dict(status='400', Error_Type='00', Error_Msg='Bad Value', Error_Field='xcode'))
        except SejNotificationMissingValue as e:
            return SejHTTPErrorResponse(
                400, 'Bad Request', dict(status='422', Error_Type='01', Error_Msg='No Data', Error_Field=e.field_name))
        except SejNotificationUnknown as e:
            return SejHTTPErrorResponse(
                422, 'Bad Request', dict(status='422', Error_Type='01', Error_Msg='Bad Value', Error_Field='X_tuchi_type'))

        return Response(body=make_sej_response(dict(status='800' if not retry_data else '810')))

    @view_config(context=Exception)
    def error(self):
        logger.exception(self.context)
        return SejHTTPErrorResponse(500, 'Internal Server Error', dict(status='500'))
