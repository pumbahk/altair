from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ticketing.views import BaseView



class SejCallback(BaseView):

    @view_config(route_name='sej.callback')
    def callback(self):




        return Response(body='tewt')