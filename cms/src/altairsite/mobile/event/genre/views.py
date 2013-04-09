# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import asc
from altairsite.config import usersite_view_config
from altaircms.topic.models import TopicTag, TopcontentTag
from altaircms.topic.api import get_topic_searcher
from altairsite.mobile.event.genre.forms import GenreForm
from altaircms.tag.models import HotWord
from altaircms.genre.searcher import GenreSearcher
from altaircms.models import Genre
from altairsite.mobile.core.helper import exist_value
from altairsite.mobile.core.helper import log_info
from altairsite.mobile.core.eventhelper import EventHelper

class ValidationFailure(Exception):
    pass

@usersite_view_config(route_name='genre', request_type="altairsite.mobile.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/genre/genre.mako')
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

    # genretree
    genre_searcher = GenreSearcher(request)
    form.dispgenre.data = request.allowable(Genre).filter(Genre.id==form.genre.data).first()
    form.genretree.data = genre_searcher.get_children(form.dispgenre.data)
    log_info("move_genre", "genretree create")

    # attention
    topcontent_searcher = get_topic_searcher(request, "topcontent")
    system_tag = topcontent_searcher.get_tag_from_genre_label(genre_tag.label)
    tag = request.allowable(TopcontentTag).filter_by(label=u"注目のイベント").first()
    if tag:
        form.attentions.data = topcontent_searcher.query_publishing_topics(datetime.now(), tag, system_tag).all()
        log_info("move_genre", "attention get")

    # Topic(Tag='トピック', system_tag='ジャンル')
    system_tag = topic_searcher.get_tag_from_genre_label(genre_tag.label)
    tag = request.allowable(TopicTag).filter_by(label=u"トピックス").first()
    if tag:
        form.topics.data = topic_searcher.query_publishing_topics(datetime.now(), tag, system_tag)
        log_info("move_genre", "topics get")

    # hotword
    today = datetime.now()
    form.hotwords.data = request.allowable(HotWord).filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end) \
             .filter_by(enablep=True).order_by(asc("display_order"), asc("term_end")).all()[0:5]
    log_info("move_genre", "hotwords get")

    log_info("move_genre", "end")

    return {
          'form':form
        , 'helper':EventHelper()
    }

@usersite_view_config(route_name='genre', context=ValidationFailure
    , request_type="altairsite.mobile.tweens.IMobileRequest", renderer='altairsite.mobile:templates/common/error.mako')
def failed_validation(request):
    return {}

