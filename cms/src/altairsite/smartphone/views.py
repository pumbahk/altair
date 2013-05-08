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

@usersite_view_config(route_name='home', request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/top.html')
def main(request):

    log_info("main", "start")
    return {
    }
