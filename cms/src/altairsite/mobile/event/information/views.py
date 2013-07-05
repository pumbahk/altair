# -*- coding: utf-8 -*-

from altaircms.datelib import get_now
from altaircms.topic.models import TopicTag
from altaircms.topic.api import get_topic_searcher
from altairsite.config import mobile_site_view_config
from altairsite.mobile.event.information.forms import InformationForm
from altairsite.mobile.core.helper import log_info, Markup
from altairsite.mobile.core.disphelper import DispHelper

@mobile_site_view_config(route_name='information', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/information/information.mako')
@mobile_site_view_config(route_name='infodetail', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/information/infodetail.mako')
def move_information(request):

    log_info("move_information", "start")
    form = InformationForm()

    #公演中止情報
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"公演中止情報").first()
    if tag is not None:
        form.informations.data = topic_searcher.query_publishing_topics(get_now(request), tag).all()
        log_info("move_information", "information get")

    log_info("move_information", "end")
    return {
          'form':form
        , 'helper':DispHelper()
    }
