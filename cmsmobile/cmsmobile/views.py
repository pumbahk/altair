# coding:utf-8
from pyramid.view import view_config
from altaircms.topic.models import TopicTag, PromotionTag
from datetime import datetime
from altaircms.topic.api import get_topic_searcher
from cmsmobile.event.search.forms import SearchForm
from altaircms.genre.searcher import GenreSearcher
from altaircms.tag.models import HotWord

@view_config(route_name='home', renderer='cmsmobile:templates/top/top.mako')
def main(request):

    # attention
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"注目のイベント").first()
    attentions = None
    if tag is not None:
        attentions = topic_searcher.query_publishing_topics(datetime.now(), tag) \
            .filter(TopicTag.organization_id == request.organization.id)[0:8]

    # pickup
    promo_searcher = get_topic_searcher(request, "promotion")
    tag = PromotionTag.query.filter_by().first()
    promotions = None
    if tag is not None:
        promotions = promo_searcher.query_publishing_topics(datetime.now(), tag) \
            .filter(PromotionTag.organization_id == request.organization.id)[0:5]

    # Topic(tag='トピック')
    tag = TopicTag.query.filter_by(label=u"トピック").first()
    topics = None
    if tag is not None:
        topics = topic_searcher.query_publishing_topics(datetime.now(), tag) \
            .filter(TopicTag.organization_id == request.organization.id)[0:5]

    # Hotward
    hotwords = HotWord.query.filter(HotWord.organization_id == request.organization.id)\
        .filter(HotWord.enablep == True)\
        .filter(HotWord.term_begin < datetime.now())\
        .filter(datetime.now() < HotWord.term_end)\
        .order_by(HotWord.display_order)[0:5]

    # Genre (Genreのリスト)
    #genre_searcher = GenreSearcher(request)
    #root = genre_searcher.get_top_genre_list()

    #for g in root:
    #    print g
    #genres = root.get_children()

    #for genre in genres:
    #    print genre

    return dict(
         topics=topics
        ,promotions=promotions
        ,attentions=attentions
        ,hotwords=hotwords
        ,form=SearchForm()
    )
