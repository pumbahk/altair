# coding:utf-8
from pyramid.view import view_config
import sqlalchemy.orm as orm

from datetime import datetime

from altaircms.topic.api import get_topic_searcher
from altaircms.genre.api import get_searcher

from altaircms.models import Genre
from altaircms.topic.models import TopcontentTag
from altaircms.tag.directives import add_tagmanager

@view_config(route_name='home', renderer='cmsmobile:templates/top/top.mako')
def main(context, request):

    #genre = Genre.query.filter_by(label=u"音楽").one()
    #tag = TopcontentTag.query.filter_by(label=u"注目のイベント").one()

    #topics = searcher.query_publishing_topics(datetime.now(), tag=tag,  system_tag=genre)

    # Genre
    #genre_searcher = get_searcher(request)
    #genres = genre_searcher.get_top_genre_list()

    # Topic
    topic_searcher = get_topic_searcher(request, context.widgettype)
    topics = topic_searcher.query_publishing_no_filtered(datetime.now())
    topics = topics.options(orm.joinedload(context.TargetTopic.tags))

    return dict(
            # genres=genres
            topics=topics
            ,topic_renderer=context.TopicHTMLRenderer(request)
        )