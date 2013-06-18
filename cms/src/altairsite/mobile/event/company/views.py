# -*- coding: utf-8 -*-

from altairsite.config import usersite_view_config
from altairsite.mobile.core.helper import log_info

@usersite_view_config(route_name='company', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/company/company.mako')
def move_company(request):
    log_info("move_company", "start")
    log_info("move_company", "end")
    return {}
