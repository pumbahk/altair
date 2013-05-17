# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config

@usersite_view_config(route_name='main',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/top.html')
def main(context, request):

    return context.get_top_render_param()
