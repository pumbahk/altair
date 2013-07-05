# -*- coding: utf-8 -*-
from altairsite.config import mobile_site_view_config
from altairsite.mobile.core.helper import log_info

@mobile_site_view_config(route_name='legal', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/legal/legal.mako')
def move_legal(request):
    log_info("move_legal", "start")
    log_info("move_legal", "end")
    return {}
