# -*- coding: utf-8 -*-
from altairsite.config import mobile_site_view_config
from altairsite.mobile.core.helper import log_info

@mobile_site_view_config(route_name='maintenance', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/maintenance/maintenance.mako')
def move_maintenance(request):
    log_info("move_maintenance", "start")
    log_info("move_maintenance", "end")
    return {}
