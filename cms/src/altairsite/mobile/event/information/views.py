# -*- coding: utf-8 -*-

from datetime import datetime
from altaircms.topic.models import TopicTag
from altaircms.topic.api import get_topic_searcher
from altairsite.config import usersite_view_config
from altairsite.mobile.event.information.forms import InformationForm
from altairsite.mobile.core.helper import log_info, Markup
from altairsite.mobile.core.disphelper import DispHelper

class ValidationFailure(Exception):
    pass

@usersite_view_config(route_name='information', request_type="altairsite.mobile.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/information/information.mako')
@usersite_view_config(route_name='infodetail', request_type="altairsite.mobile.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/information/infodetail.mako')
def move_information(request):

    log_info("move_information", "start")
    form = InformationForm()

    #公演中止情報
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"公演中止情報").first()
    if tag is not None:
        form.informations.data = topic_searcher.query_publishing_topics(datetime.now(), tag).all()
        log_info("move_information", "information get")

    log_info("move_information", "end")
    return {
          'form':form
        , 'helper':DispHelper()
    }
