# -*- coding: utf-8 -*-
from pyramid.view import (
    view_config,
    view_defaults,
    )
from altair.pyramid_dynamic_renderer import lbr_view_config


@view_defaults(route_name='famiport.ping', renderer='json')
class PingPongView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method='GET')
    def get(self):
        return {}
