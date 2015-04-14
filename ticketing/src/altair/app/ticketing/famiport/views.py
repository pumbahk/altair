# -*- coding: utf-8 -*-
from pyramid.view import (
    view_config,
    view_defaults,
    )
from altair.pyramid_dynamic_renderer import lbr_view_config


@view_defaults(route_name='famiport.api.search', renderer='json')
class SearchView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method='GET')
    def post(self):
        return {}
