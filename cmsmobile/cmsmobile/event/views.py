# -*- coding: utf-8 -*-

from pyramid.url import route_path
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from altaircms.topic.models import TopicTag, PromotionTag
from altaircms.models import Performance
import webhelpers.paginate as paginate
from datetime import datetime
from altaircms.topic.api import get_topic_searcher
from cmsmobile.event.forms import SearchForm
from ticketing.models import merge_session_with_post

@view_config(route_name='genre', renderer='cmsmobile:templates/genre/genre.mako')
def move_genre(request):

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
        ,form=SearchForm()
        ,genre=genre
        ,subgenre=subgenre
        ,promotions=promotions
        ,attentions=attentions
    )

@view_config(route_name='search', renderer='cmsmobile:templates/search/search.mako')
def search(request):

    num = 0
    performances = None
    form = SearchForm(request.POST)
    if not form.validate():
        return {
            'num':num
            ,'performances':performances
            ,'form':form
        }

    qs = None
    word = form.word.data
    if word:
        qs = Performance.query.filter_by()
        likeword = u"%%%s%%" % word
        qs = qs.filter((Performance.title.like(likeword)) | (Performance.venue.like(likeword))).all()

    if qs:
        performances = paginate.Page(
            qs,
            page=int(request.params.get('page', 0)),
            items_per_page=5,
            url=paginate.PageURL_WebOb(request)
            )
        num = len(qs)

    #area = int(request.params.get("area", 0))
    #if area:
    #    pass

    return {
         'num':num
        ,'word':word
        ,'performances':performances
        ,'form':SearchForm()
    }

@view_config(route_name='genresearch', renderer='cmsmobile:templates/genresearch/genresearch.mako')
def genresearch(request):

    genre = request.params.get("genre", None)
    subgenre = request.params.get("subgenre", None)

    num = 0
    performances = None
    form = SearchForm(request.POST)
    if not form.validate():
        return {
             'genre':genre
            ,'subgenre':subgenre
            ,'num':num
            ,'performances':performances
            ,'form':form
        }

    qs = None
    word = form.word.data
    if word:
        qs = Performance.query.filter_by()
        likeword = u"%%%s%%" % word
        qs = qs.filter((Performance.title.like(likeword)) | (Performance.venue.like(likeword))).all()

    if qs:
        performances = paginate.Page(
            qs,
            page=int(request.params.get('page', 0)),
            items_per_page=5,
            url=paginate.PageURL_WebOb(request)
        )
        num = len(qs)

    #area = int(request.params.get("area", 0))
    #if area:
    #    pass

    return {
         'genre':genre
        ,'subgenre':subgenre
        ,'num':num
        ,'word':word
        ,'performances':performances
        ,'form':SearchForm()
    }

@view_config(route_name='detail', renderer='cmsmobile:templates/detail/detail.mako')
def move_detail(request):
    event_id = request.params.get("event_id", None)
    return {
    }

@view_config(route_name='information', renderer='cmsmobile:templates/information/information.mako')
def move_information(request):
    #公演中止情報
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"公演中止情報").first()
    informations = None
    if tag is not None:
        informations = topic_searcher.query_publishing_topics(datetime.now(), tag)

    return dict(
        informations=informations
    )

@view_config(route_name='help', renderer='cmsmobile:templates/help/help.mako')
def move_help(request):
    return {
    }
