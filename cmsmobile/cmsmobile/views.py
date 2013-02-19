# coding:utf-8
from pyramid.view import view_config

from altaircms.genre.api import GenreSearcher

from altaircms.models import Genre
from altaircms.topic.models import TopicTag, PromotionTag
from altaircms.tag.directives import add_tagmanager

from datetime import datetime
import sqlalchemy.orm as orm
from altaircms.topic.api import get_topic_searcher


@view_config(route_name='home', renderer='cmsmobile:templates/top/top.mako')
def main(context, request):


    #tag = TopcontentTag.query.filter_by(label=u"注目のイベント").one()
    #topics = searcher.query_publishing_topics(datetime.now(), tag=tag,  system_tag=genre)

    # pickup

    # Genre (Genreのリスト)
    #genre_searcher = GenreSearcher(request)
    #root = genre_searcher.query_genre_root()
    #genres = root.get_children()

    # attention
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"注目のイベント").first()
    attentions = None
    if tag is not None:
        attentions = topic_searcher.query_publishing_topics(datetime.now(), tag)[0:8]

    # pickup
    promo_searcher = get_topic_searcher(request, "promotion")
    tag = PromotionTag.query.filter_by().first()
    promotions = None
    if tag is not None:
        promotions = promo_searcher.query_publishing_topics(datetime.now(), tag)[0:5]

    # Topic(tag='トピック')
    tag = TopicTag.query.filter_by(label=u"トピック").first()
    topics = None
    if tag is not None:
        topics = topic_searcher.query_publishing_topics(datetime.now(), tag)[0:5]

    # Hotward

    return dict(
         topics=topics
        ,promotions=promotions
        ,attentions=attentions
    )
