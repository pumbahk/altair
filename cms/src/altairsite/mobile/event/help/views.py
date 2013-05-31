# -*- coding: utf-8 -*-

from datetime import datetime
from altaircms.topic.models import TopicTag
from altaircms.topic.api import get_topic_searcher
from altairsite.config import usersite_view_config
from altairsite.mobile.event.help.forms import HelpForm
from altairsite.mobile.core.helper import log_info
from altairsite.mobile.core.disphelper import DispHelper

class ValidationFailure(Exception):
    pass

@usersite_view_config(route_name='help', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/help/help.mako')
def move_help(request):

    log_info("move_help", "start")
    form = HelpForm()

    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"質問").first()

    if tag is not None:
        form.helps.data = topic_searcher.query_publishing_topics(datetime.now(), tag).all()
        log_info("move_help", "helps get")

    log_info("move_help", "start")
    return {
          'form':form
        , 'helper':DispHelper()
    }
