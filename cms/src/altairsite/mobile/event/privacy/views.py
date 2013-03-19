# -*- coding: utf-8 -*-
from pyramid.view import view_config
from cmsmobile.core.helper import log_info

@view_config(route_name='privacy', request_type="altairsite.mobile.tweens.IMobileRequest"
    , renderer='cmsmobile:templates/privacy/privacy.mako')
def move_privacy_policy(request):
    log_info("move_privacy_policy", "start")
    log_info("move_privacy_policy", "end")
    return {}