# -*- coding: utf-8 -*-

from altaircms.datelib import get_now
from altaircms.topic.models import TopicTag, Topic
from altaircms.topic.api import get_topic_searcher
from altairsite.config import mobile_site_view_config
from altairsite.mobile.event.information.forms import InformationForm
from altairsite.mobile.core.helper import log_info, Markup
from altairsite.mobile.core.disphelper import DispHelper
from altairsite.separation import selectable_renderer

@mobile_site_view_config(route_name='information', request_type="altair.mobile.interfaces.IMobileRequest"
    , renderer=selectable_renderer('altairsite.mobile:templates/%(prefix)s/information/information.mako'))
def move_information(request):

    log_info("move_information", "start")
    form = InformationForm()

    #公演中止情報
    topic_searcher = get_topic_searcher(request, "topic")
    tag = request.allowable(TopicTag).filter_by(label=u"公演中止情報").first()
    if tag is not None:
        form.informations.data = topic_searcher.query_publishing(get_now(request), tag).all()
        log_info("move_information", "information get")

    log_info("move_information", "end")
    return {
          'form':form
        , 'helper':DispHelper()
    }

@mobile_site_view_config(route_name='infodetail', request_type="altair.mobile.interfaces.IMobileRequest"
    , renderer=selectable_renderer('altairsite.mobile:templates/%(prefix)s/information/infodetail.mako'))
def move_detail_information(request):

    log_info("move_detail_information", "start")
    form = InformationForm(request.GET)

    #公演中止情報
    topic_searcher = get_topic_searcher(request, "topic")
    tag = request.allowable(TopicTag).filter_by(label=u"公演中止情報").first()
    if tag is not None:
        form.information.data = topic_searcher.query_publishing(get_now(request), tag) \
            .filter(Topic.id==form.information_id.data).first()
        log_info("move_information", "information detail get")

    log_info("move_detail_information", "end")
    return {
          'form':form
        , 'helper':DispHelper()
    }
