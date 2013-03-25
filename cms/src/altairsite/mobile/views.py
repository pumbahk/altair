# coding:utf-8
from datetime import datetime
from pyramid.view import view_config
from altaircms.topic.models import TopicTag, PromotionTag, TopcontentTag
from altaircms.topic.api import get_topic_searcher
from altaircms.genre.searcher import GenreSearcher
from altaircms.tag.models import HotWord
from altairsite.mobile.forms import TopForm
from sqlalchemy import asc
from core.helper import log_info
from altairsite.mobile.core.eventhelper import EventHelper

@view_config(route_name='home', request_type="altairsite.mobile.tweens.IMobileRequest"
             , renderer='altairsite.mobile:templates/top/top.mako')
def main(request):

    log_info("main", "start")

    form = TopForm()

    topcontent_searcher = get_topic_searcher(request, "topcontent")
    tag = TopcontentTag.query.filter_by(label=u"注目のイベント").first()
    if tag:
        form.attentions.data = topcontent_searcher.query_publishing_topics(datetime.now(), tag)[0:8]
        log_info("main", "attensions get")

    promo_searcher = get_topic_searcher(request, "promotion")
    tag = PromotionTag.query.filter_by(label=u"プロモーション枠").first()
    if tag:
        form.promotions.data = promo_searcher.query_publishing_topics(datetime.now(), tag)[0:5]
        log_info("main", "promotions get")

    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"トピックス").first()
    if tag:
        form.topics.data = topic_searcher.query_publishing_topics(datetime.now(), tag)[0:5]
        log_info("main", "topics get")

    today = datetime.now()
    form.hotwords.data = request.allowable(HotWord).filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end) \
            .filter_by(enablep=True).order_by(asc("display_order"), asc("term_end")).all()[0:5]
    log_info("main", "hotwords get")

    genre_searcher = GenreSearcher(request)
    form.genretree.data = genre_searcher.root.children
    log_info("main", "genretree get")

    log_info("main", "end")

    return {
         'form':form
        ,'helper':EventHelper()
    }
