# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.smartphone.common.helper import SmartPhoneHelper

@usersite_view_config(route_name='main',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/top.html')
def main(context, request):
    promotions = context.search(request=request, kind="promotion", system_tag_id=None)[0:5]
    topcontents = context.search(request=request, kind="topcontent", system_tag_id=None)[0:5]
    topics = context.search(request=request, kind="topic", system_tag_id=None)[0:5]
    hotwords = context.get_hotword(request=request)[0:5]
    genretree = context.get_genre_tree(request=request, parent=None)
    regions = context.get_region()
    helper = SmartPhoneHelper()

    return {
         'promotions':promotions
        ,'topcontents':topcontents
        ,'topics':topics
        ,'hotwords':hotwords
        ,'genretree':genretree
        ,'regions':regions
        ,'helper':helper
    }
