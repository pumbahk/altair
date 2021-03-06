# -*- coding:utf-8 -*-
from sqlalchemy import asc
from altaircms.topic.models import TopicTag, PromotionTag, TopcontentTag
from altaircms.topic.api import get_topic_searcher
from altaircms.genre.searcher import GenreSearcher
from altaircms.tag.models import HotWord
from altairsite.config import mobile_site_view_config
from altairsite.mobile.forms import TopForm
from altairsite.mobile.core.helper import log_info
from altairsite.mobile.core.eventhelper import EventHelper
from altaircms.datelib import get_now
from altairsite.separation import selectable_renderer, get_organization_from_request

@mobile_site_view_config(route_name='home', request_type="altair.mobile.interfaces.IMobileRequest"
             , renderer=selectable_renderer('altairsite.mobile:templates/%(prefix)s/top/top.mako'))
def main(request):

    log_info("main", "start")

    form = TopForm()

    org = get_organization_from_request(request)
    topcontent_searcher = get_topic_searcher(request, "topcontent")
    tag = request.allowable(TopcontentTag).filter_by(label=u"注目のイベント").first()
    if tag:
        if org.short_name == 'RT':
            form.attentions.data = topcontent_searcher.query_publishing_topics(get_now(request), tag)[0:8]
        else:
            form.attentions.data = topcontent_searcher.query_publishing_topics(get_now(request), tag).all()
        log_info("main", "attensions get")

    promo_searcher = get_topic_searcher(request, "promotion")
    tag = request.allowable(PromotionTag).filter_by(label=u"プロモーション枠").first()
    if tag:
        if org.short_name == 'RT':
            form.promotions.data = promo_searcher.query_publishing_topics(get_now(request), tag)[0:5]
        else:
            form.promotions.data = promo_searcher.query_publishing_topics(get_now(request), tag).all()
        log_info("main", "promotions get")

    topic_searcher = get_topic_searcher(request, "topic")
    tag = request.allowable(TopicTag).filter_by(label=u"トピックス").first()
    if tag:
        if org.short_name == 'RT':
            form.topics.data = topic_searcher.query_publishing_topics(get_now(request), tag)[0:5]
        else:
            form.topics.data = topic_searcher.query_publishing_topics(get_now(request), tag).all()
        log_info("main", "topics get")

    today = get_now(request)
    if org.short_name == 'RT':
        form.hotwords.data = request.allowable(HotWord).filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end) \
                .filter_by(enablep=True).order_by(asc("display_order"), asc("term_end")).all()[0:5]
    else:
        form.hotwords.data = request.allowable(HotWord).filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end) \
                .filter_by(enablep=True).order_by(asc("display_order"), asc("term_end")).all()
    log_info("main", "hotwords get")

    genre_searcher = GenreSearcher(request)
    if genre_searcher.root:
        form.genretree.data = genre_searcher.root.children

    log_info("main", "genretree get")

    log_info("main", "end")

    return {
         'form':form
        ,'helper':EventHelper()
    }
