# -*- coding: utf-8 -*-

from altaircms.datelib import get_now
from altaircms.topic.models import TopicTag
from altaircms.topic.api import get_topic_searcher
from altairsite.config import mobile_site_view_config
from altairsite.mobile.event.help.forms import HelpForm
from altairsite.mobile.core.helper import log_info
from altairsite.mobile.core.disphelper import DispHelper
from altairsite.separation import selectable_renderer

@mobile_site_view_config(route_name='help', request_type="altair.mobile.interfaces.IMobileRequest"
    , renderer=selectable_renderer('altairsite.mobile:templates/%(prefix)s/help/help.mako'))
def move_help(request):

    log_info("move_help", "start")
    form = HelpForm()

    topic_searcher = get_topic_searcher(request, "topic")
    tag = request.allowable(TopicTag).filter_by(label=u"質問").first()

    if tag is not None:
        form.helps.data = topic_searcher.query_publishing_topics(get_now(request), tag).all()
        log_info("move_help", "helps get")

    log_info("move_help", "start")
    return {
          'form':form
        , 'helper':DispHelper()
    }
