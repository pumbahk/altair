# -*- coding: utf-8 -*-

from pyramid.view import view_config

@view_config(route_name='admin.event.index', renderer='ticketing:templates/event/index.html')
def index(context, request):
    return {}
