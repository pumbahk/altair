# -*- coding: utf-8 -*-
from altairsite.config import mobile_site_view_config
from altairsite.mobile.core.helper import log_info
from altairsite.separation import selectable_renderer

@mobile_site_view_config(route_name='privacy', request_type="altair.mobile.interfaces.IMobileRequest"
    , renderer=selectable_renderer('altairsite.mobile:templates/%(prefix)s/privacy/privacy.mako'))
def move_privacy_policy(request):
    log_info("move_privacy_policy", "start")
    log_info("move_privacy_policy", "end")
    return {}
