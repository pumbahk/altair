# coding:utf-8
from pyramid.view import view_config

from altaircms.genre.api import GenreSearcher

from altaircms.models import Genre
from altaircms.topic.models import TopcontentTag
from altaircms.tag.directives import add_tagmanager

from datetime import datetime
import sqlalchemy.orm as orm
from altaircms.topic.api import get_topic_searcher


@view_config(route_name='home', renderer='cmsmobile:templates/top/top.mako')
def main(context, request):

    genre = Genre.query.filter_by(label=u"音楽").one()
    #tag = TopcontentTag.query.filter_by(label=u"注目のイベント").one()
    #topics = searcher.query_publishing_topics(datetime.now(), tag=tag,  system_tag=genre)

    # pickup

    # Genre (Genreのリスト)
    #genre_searcher = GenreSearcher(request)
    #root = genre_searcher.query_genre_root()
    #genres = root.get_children()

    # Topic
    topic_searcher = get_topic_searcher(request, context.widgettype)
    topics = topic_searcher.query_publishing_no_filtered(datetime.now())
    topics = topics.options(orm.joinedload(context.TargetTopic.tags))[0:5]

    # Hotward

    return dict(
        topics=topics
    )

