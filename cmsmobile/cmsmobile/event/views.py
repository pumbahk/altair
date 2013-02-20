# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults

from cmsmobile.core.views import BaseView
from altaircms.models import Genre
from altaircms.topic.models import TopicTag, PromotionTag

import webhelpers.paginate as paginate
from datetime import datetime
import sqlalchemy.orm as orm
from altaircms.topic.api import get_topic_searcher


@view_config(route_name='genre', renderer='cmsmobile:templates/genre/genre.mako')
def move_genre(request):
    current_page = int(request.params.get("page", 0))
    page_url = paginate.PageURL_WebOb(request)

    # genre
    genre = request.params.get("genre", None)
    subgenre = request.params.get("subgenre", None)
    system_tag = TopicTag.query.filter_by(label=genre).one()
    if (subgenre is not None):
        system_tag = TopicTag.query.filter_by(label=subgenre).one()

    # attention
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"注目のイベント").first()
    attentions = None
    if tag is not None:
        attentions = topic_searcher.query_publishing_topics(datetime.now(), tag, system_tag)

    # pickup
    promo_searcher = get_topic_searcher(request, "promotion")
    tag = PromotionTag.query.filter_by().first()
    promotions = None
    if tag is not None:
        promotions = promo_searcher.query_publishing_topics(datetime.now(), tag, system_tag)

    # Topic(Tag='トピック', system_tag='ジャンル')
    tag = TopicTag.query.filter_by(label=u"トピック").first()
    topics = None
    if tag is not None:
        topics = topic_searcher.query_publishing_topics(datetime.now(), tag, system_tag)

    return dict(
         topics=topics
        ,genre=genre
        ,subgenre=subgenre
        ,promotions=promotions
        ,attentions=attentions
    )

@view_config(route_name='search', renderer='cmsmobile:templates/search/search.mako')
def search(request):
    current_page = int(request.params.get("page", 0))

    word = request.params.get("word", 0)
    if word:
        pass
    area = int(request.params.get("area", 0))
    if area:
        pass

    return {

    }

@view_config(route_name='detail', renderer='cmsmobile:templates/detail/detail.mako')
def move_detail(request):
    event_id = request.params.get("event_id", None)
    return {
    }

@view_config(route_name='inquiry', renderer='cmsmobile:templates/inquiry/inquiry.mako')
def move_inquiry(request):
    return {
    }

@view_config(route_name='help', renderer='cmsmobile:templates/help/help.mako')
def move_help(request):
    return {
    }

@view_config(route_name='order', renderer='cmsmobile:templates/order/order.mako')
def move_order(request):
    return {
    }

