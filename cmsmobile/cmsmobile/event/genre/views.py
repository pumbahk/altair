# -*- coding: utf-8 -*-

from pyramid.view import view_config
from altaircms.topic.models import TopicTag, PromotionTag
from datetime import datetime
from altaircms.topic.api import get_topic_searcher
from cmsmobile.event.search.forms import SearchForm
from altaircms.tag.models import HotWord

class ValidationFailure(Exception):
    pass

@view_config(route_name='genre', renderer='cmsmobile:templates/genre/genre.mako')
def move_genre(request):

    # init
    form = SearchForm(request.GET)
    form.path.data = "/genresearch"
    form.num.data = "0"
    form.page.data = "1"
    form.page_num.data = "0"

    # genre
    system_tag = TopicTag.query.filter_by(label=form.genre.data).one()
    if form.sub_genre.data != "":
        system_tag = TopicTag.query.filter_by(label=form.sub_genre.data).one()

    # attention
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"注目のイベント").first()
    attentions = None
    if tag is not None:
        attentions = topic_searcher.query_publishing_topics(datetime.now(), tag, system_tag) \
            .filter(TopicTag.organization_id == request.organization.id)

    # pickup
    promo_searcher = get_topic_searcher(request, "promotion")
    tag = PromotionTag.query.filter_by().first()
    promotions = None
    if tag is not None:
        promotions = promo_searcher.query_publishing_topics(datetime.now(), tag, system_tag) \
            .filter(PromotionTag.organization_id == request.organization.id)

    # Topic(Tag='トピック', system_tag='ジャンル')
    tag = TopicTag.query.filter_by(label=u"トピック").first()
    topics = None
    if tag is not None:
        topics = topic_searcher.query_publishing_topics(datetime.now(), tag, system_tag) \
            .filter(TopicTag.organization_id == request.organization.id)

    # hotword
    hotwords = HotWord.query.filter(HotWord.organization_id == request.organization.id) \
                   .filter(HotWord.enablep == True) \
                   .filter(HotWord.term_begin < datetime.now()) \
                   .filter(datetime.now() < HotWord.term_end) \
                   .order_by(HotWord.display_order)[0:5]

    return dict(
         form=form
        ,topics=topics
        ,promotions=promotions
        ,attentions=attentions
        ,hotwords=hotwords
    )
