# -*- coding: utf-8 -*-

from pyramid.view import view_config
from altaircms.topic.models import TopicTag, PromotionTag
from datetime import datetime
from altaircms.topic.api import get_topic_searcher
from cmsmobile.event.genre.forms import GenreForm
from altaircms.tag.models import HotWord
from altaircms.genre.searcher import GenreSearcher
from altaircms.models import Genre
from cmsmobile.core.helper import exist_value

class ValidationFailure(Exception):
    pass

@view_config(route_name='genre', renderer='cmsmobile:templates/genre/genre.mako')
def move_genre(request):

    # init
    form = GenreForm(request.GET)
    form.path.data = "/genresearch"
    form.num.data = "0"
    form.page.data = "1"
    form.page_num.data = "0"

    # genre
    system_tag = request.allowable(Genre).filter(Genre.id==form.genre.data).first()
    if exist_value(form.sub_genre.data):
        system_tag = request.allowable(Genre).filter(Genre.id==form.sub_genre.data).first()
        form.dispsubgenre.data = request.allowable(Genre).filter(Genre.id==form.sub_genre.data).first()

    if not system_tag:
        raise ValidationFailure

    # genretree
    genre_searcher = GenreSearcher(request)
    form.dispgenre.data = request.allowable(Genre).filter(Genre.id==form.genre.data).first()
    form.genretree.data = genre_searcher.get_children(form.dispgenre.data)

    # attention
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"注目のイベント").first()
    if tag is not None:
        form.attentions.data = topic_searcher.query_publishing_topics(datetime.now(), tag, system_tag)

    # pickup
    promo_searcher = get_topic_searcher(request, "promotion")
    tag = PromotionTag.query.filter_by().first()
    if tag is not None:
        form.promotions.data = promo_searcher.query_publishing_topics(datetime.now(), tag, system_tag)

    # Topic(Tag='トピック', system_tag='ジャンル')
    tag = TopicTag.query.filter_by(label=u"トピック").first()
    if tag is not None:
        form.topics.data = topic_searcher.query_publishing_topics(datetime.now(), tag, system_tag)

    # hotword
    form.hotwords.data = HotWord.query.filter(HotWord.organization_id == request.organization.id) \
                   .filter(HotWord.enablep == True) \
                   .filter(HotWord.term_begin < datetime.now()) \
                   .filter(datetime.now() < HotWord.term_end) \
                   .order_by(HotWord.display_order)[0:5]

    return {'form':form}

@view_config(route_name='genre', context=ValidationFailure, renderer='cmsmobile:templates/common/error.mako')
def failed_validation(request):
    return {}

