from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import HTTPClientError

from .resources import SejResponseError
from .payment import callback_notification
from .models import SejOrder

import traceback
import logging

class SejHTTPErrorResponse(HTTPClientError):

    empty_body = True

    def __init__(self, sej_error):
        self.code = sej_error.code
        super(HTTPClientError, self).__init__()
        self.body = sej_error.response()

class SejCallback(object):

    log = logging.getLogger(__file__)
    log_sej = logging.getLogger('sej_payment')

    def __init__(self, request):
        self.request = request

    @view_config(route_name='sej.callback.form', renderer="ticketing:sej/template/index.html")
    def callback_form(self):
        return {}

    @view_config(route_name='sej.callback')
    def callback(self):
        try:

            self.log_sej.info('[callback]' % self.request.body)
            self.request = self.request.decode('CP932')

            response = callback_notification(self.request.POST)
        except SejResponseError, e:
           raise SejHTTPErrorResponse(e)
        except Exception, de:

            self.log.error(de)
            self.log.error(traceback.format_exc())

            e = SejResponseError(
                500, 'Internal Server Error', dict(status='500')) 
            raise SejHTTPErrorResponse(e)
        return Response(body=response)
