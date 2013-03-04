# -*- coding: utf-8 -*-

from pyramid.view import view_config

class ValidationFailure(Exception):
    pass

@view_config(route_name='company', renderer='cmsmobile:templates/company/company.mako')
def move_company(request):
    return {}
