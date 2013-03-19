# -*- coding: utf-8 -*-
from pyramid.view import view_config
from cmsmobile.core.helper import log_info

@view_config(route_name='legal', request_type="altairsite.mobile.tweens.IMobileRequest"
    , renderer='cmsmobile:templates/legal/legal.mako')
def move_legal(request):
    log_info("move_legal", "start")
    log_info("move_legal", "end")
    return {}
