# -*- coding: utf-8 -*-

from pyramid.view import view_config

@view_config(route_name='admin.manager.index', renderer='ticketing:templates/manager/index.html')
def index(context, request):
    managers = []
    return {
        'managers' : managers
    }

@view_config(route_name='admin.manager.new', renderer='ticketing:templates/manager/new.html')
def new(context, request):
    return {}