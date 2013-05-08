# -*- coding:utf-8 -*-
from datetime import datetime
from sqlalchemy import asc
from altaircms.topic.models import TopicTag, PromotionTag, TopcontentTag
from altaircms.topic.api import get_topic_searcher
from altaircms.genre.searcher import GenreSearcher
from altaircms.tag.models import HotWord
from altairsite.config import usersite_view_config
from altairsite.mobile.forms import TopForm
from altairsite.mobile.core.helper import log_info
from altairsite.mobile.core.eventhelper import EventHelper

@usersite_view_config(route_name='main',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/top.html')
def main(context, request):
    promotions = context.search(request=request, kind="promotion", system_tag_id=None)[0:5]
    topcontents = context.search(request=request, kind="topcontent", system_tag_id=None)[0:5]
    topics = context.search(request=request, kind="topic", system_tag_id=None)[0:5]
    hotwords = context.getHotword(request=request)[0:5]

    return {
         'promotions':promotions
        ,'topcontents':topcontents
        ,'topics':topics
        ,'hotwords':hotwords
    }
