# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.smartphone.event.search.forms import TopSearchForm

@usersite_view_config(route_name='main',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/top.html')
def main(context, request):
    promotions = context.getInfo(kind="promotion", system_tag_id=None)[0:5]
    topcontents = context.getInfo(kind="topcontent", system_tag_id=None)[0:5]
    topics = context.getInfo(kind="topic", system_tag_id=None)[0:5]
    hotwords = context.get_hotword()[0:5]
    genretree = context.get_genre_tree(parent=None)
    areas = context.get_area()
    helper = SmartPhoneHelper()

    return {
         'promotions':promotions
        ,'topcontents':topcontents
        ,'topics':topics
        ,'hotwords':hotwords
        ,'genretree':genretree
        ,'areas':areas
        ,'helper':helper
        ,'form':TopSearchForm()
    }
