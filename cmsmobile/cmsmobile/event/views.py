# -*- coding: utf-8 -*-

from cmsmobile.solr import helper
from pyramid.view import view_config
from altaircms.topic.models import TopicTag, PromotionTag
import webhelpers.paginate as paginate
from datetime import datetime
from altaircms.topic.api import get_topic_searcher
from cmsmobile.event.forms import SearchForm
from pyramid.httpexceptions import HTTPNotFound
from altaircms.event.models import Event

import logging

logger = logging.getLogger(__file__)

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

    return dict(
         form=form
        ,topics=topics
        ,promotions=promotions
        ,attentions=attentions
    )

@view_config(route_name='search', renderer='cmsmobile:templates/search/search.mako')
@view_config(route_name='genresearch', renderer='cmsmobile:templates/genresearch/genresearch.mako')
def search(request):

    form = SearchForm(request.GET)

    # freeword, genre, subgenre
    events = _freeword_search(request, form)

    # area
    if form.area.data:
        #events = _area_search(request, form)
        pass

    # paging
    if events:
        form.num.data = len(events)
        items_per_page = 10
        events = paginate.Page(
            events,
            form.page.data,
            items_per_page,
            url=paginate.PageURL_WebOb(request)
        )
        if form.num.data % items_per_page == 0:
            form.page_num.data = form.num.data / items_per_page
        else:
            form.page_num.data = form.num.data / items_per_page + 1

    return {
        'events':events
        ,'form':form
    }


@view_config(route_name='detail', renderer='cmsmobile:templates/detail/detail.mako')
def move_detail(request):
    event_id = request.params.get("event_id", None)
    event = Event.query.filter(Event.id == event_id).first()
    if not event:
        raise ValidationFailure
    return {
        'event':event
    }

@view_config(route_name='detail', context=ValidationFailure, renderer='cmsmobile:templates/common/error.mako')
def failed_validation(request):
    return {}

@view_config(route_name='information', renderer='cmsmobile:templates/information/information.mako')
def move_information(request):
    #公演中止情報
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"公演中止情報").first()
    informations = None
    if tag is not None:
        informations = topic_searcher.query_publishing_topics(datetime.now(), tag)\
            .filter(TopicTag.organization_id == request.organization.id)

    return dict(
        informations=informations
    )

@view_config(route_name='help', renderer='cmsmobile:templates/help/help.mako')
def move_help(request):
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"質問").first()

    helps = None
    if tag is not None:
        helps = topic_searcher.query_publishing_topics(datetime.now(), tag)\
            .filter(TopicTag.organization_id == request.organization.id)

    return dict(
        helps=helps
    )

def _area_search(request, form):
    search_word = ""
    if form.sub_genre.data != "" and form.sub_genre.data is not None:
        search_word = form.word.data + " " + form.sub_genre.data
    elif form.genre.data != "" and form.genre.data is not None:
        search_word = form.word.data + " " + form.genre.data

    # ジャンルが渡された場合は、全文検索を実行してから地域検索
    events = []
    if search_word != "":
        try:
            events = helper.searchEvents(request, search_word)
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound
    else:
        #地域検索
        if events:
            form.num.data = len(events)
            items_per_page = 10
            events = paginate.Page(
                events,
                form.page.data,
                items_per_page,
                url=paginate.PageURL_WebOb(request)
            )
            if form.num.data % items_per_page == 0:
                form.page_num.data = form.num.data / items_per_page
            else:
                form.page_num.data = form.num.data / items_per_page + 1

    return {
        'events':events
        ,'form':form
    }


def _freeword_search(request, form):

    search_word = form.word.data
    if form.sub_genre.data != "" and form.sub_genre.data is not None:
        search_word = form.word.data + " " + form.sub_genre.data
    elif form.genre.data != "" and form.genre.data is not None:
        search_word = form.word.data + " " + form.genre.data

    events = []
    if search_word != "":
        try:
            events = helper.searchEvents(request, search_word)
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound
    return events
