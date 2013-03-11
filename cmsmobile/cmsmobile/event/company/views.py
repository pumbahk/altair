# -*- coding: utf-8 -*-

from pyramid.view import view_config
from cmsmobile.core.helper import log_info

@view_config(route_name='company', renderer='cmsmobile:templates/company/company.mako')
def move_company(request):
    log_info("move_company", "start")
    log_info("move_company", "end")
    return {}
