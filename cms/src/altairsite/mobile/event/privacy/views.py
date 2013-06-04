# -*- coding: utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.mobile.core.helper import log_info

@usersite_view_config(route_name='privacy', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/privacy/privacy.mako')
def move_privacy_policy(request):
    log_info("move_privacy_policy", "start")
    log_info("move_privacy_policy", "end")
    return {}
