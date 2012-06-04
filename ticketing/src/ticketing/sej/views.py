from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import HTTPClientError

from .resources import SejResponseError
from .payment import callback_notification
from .models import SejOrder

class SejHTTPErrorResponse(HTTPClientError):

    code = 500
    title = 'Error'
    empty_body = True

    def __init__(self, sej_error):
        super(HTTPClientError, self).__init__()
        self.body = sej_error.response()

class SejCallback(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='sej.index', renderer='ticketing:sej/template/index.html')
    def index(self):
        list = SejOrder.all()
        return dict(
            list = list
        )

    @view_config(route_name='sej.callback')
    def callback(self):
        try:
            response = callback_notification(self.request.POST)
        except SejResponseError, e:
           raise SejHTTPErrorResponse(e)
        return Response(body=response)