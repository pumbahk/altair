from pyramid.view import view_config, view_defaults
from pyramid.response import Response

from ticketing.views import BaseView


from pyramid.httpexceptions import HTTPClientError
from string import Template

from .payment import callback_notification
from . import SejResponseError
from .models import SejOrder

class SejHTTPErrorResponse(HTTPClientError):

    code = 500
    title = 'Error'

    def __init__(self, sej_error):
        self.code = sej_error.code
        self.title = sej_error.reason

        super(HTTPClientError, self).__init__()
        self.body = sej_error.response()

class SejCallback(BaseView):

    @view_config(route_name='sej.index', renderer='ticketing:sej/template/index.html')
    def index(self):
        list = SejOrder.all()
        return dict(
            list = list
        )

    @view_config(route_name='sej.request')
    def request(self):
        pass

    @view_config(route_name='sej.callback')
    def callback(self):
        try:
            response = callback_notification(self.request.POST)
        except SejResponseError, e:
           raise SejHTTPErrorResponse(e)
        return Response(body=response)