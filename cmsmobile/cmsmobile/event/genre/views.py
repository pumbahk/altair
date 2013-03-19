# -*- coding: utf-8 -*-

from pyramid.view import view_config
from altaircms.topic.models import TopicTag
from datetime import datetime
from altaircms.topic.api import get_topic_searcher
from cmsmobile.event.genre.forms import GenreForm
from altaircms.tag.models import HotWord
from altaircms.genre.searcher import GenreSearcher
from altaircms.models import Genre
from cmsmobile.core.helper import exist_value
from sqlalchemy import asc
from cmsmobile.core.helper import log_info

class ValidationFailure(Exception):
    pass

@view_config(route_name='genre', request_type="altairsite.mobile.tweens.IMobileRequest"
    , renderer='cmsmobile:templates/genre/genre.mako')
def move_genre(request):

    log_info("move_genre", "start")

    # init
    form = GenreForm(request.GET)
    form.path.data = "/genresearch"
    form.num.data = "0"
    form.page.data = "1"
    form.page_num.data = "0"

    # genre
    topic_searcher = get_topic_searcher(request, "topic")
    genre_tag = request.allowable(Genre).filter(Genre.id==form.genre.data).first()
    if exist_value(form.sub_genre.data):
        genre_tag = request.allowable(Genre).filter(Genre.id==form.sub_genre.data).first()
        form.dispsubgenre.data = request.allowable(Genre).filter(Genre.id==form.sub_genre.data).first()
        log_info("move_genre", "genre get")

    if not genre_tag:
        log_info("move_genre", "genre not found")
        raise ValidationFailure

    system_tag = topic_searcher.get_tag_from_genre_label(genre_tag.label)

    # genretree
    genre_searcher = GenreSearcher(request)
    form.dispgenre.data = request.allowable(Genre).filter(Genre.id==form.genre.data).first()
    form.genretree.data = genre_searcher.get_children(form.dispgenre.data)
    log_info("move_genre", "genretree create")

    # attention
    tag = TopicTag.query.filter_by(label=u"注目のイベント").first()
    if tag:
        form.attentions.data = topic_searcher.query_publishing_topics(datetime.now(), tag, system_tag).all()
        log_info("move_genre", "attention get")

    # Topic(Tag='トピック', system_tag='ジャンル')
    tag = TopicTag.query.filter_by(label=u"トピック").first()
    if tag:
        form.topics.data = topic_searcher.query_publishing_topics(datetime.now(), tag, system_tag)
        log_info("move_genre", "topics get")

    # hotword
    today = datetime.now()
    form.hotwords.data = request.allowable(HotWord).filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end) \
             .filter_by(enablep=True).order_by(asc("display_order"), asc("term_end")).all()[0:5]
    log_info("move_genre", "hotwords get")

    log_info("move_genre", "end")
    return {'form':form}

@view_config(route_name='genre', context=ValidationFailure
    , request_type="altairsite.mobile.tweens.IMobileRequest", renderer='cmsmobile:templates/common/error.mako')
def failed_validation(request):
    return {}

