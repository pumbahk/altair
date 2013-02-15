# coding:utf-8
from pyramid.view import view_config

from datetime import datetime

from altaircms.topic.api import get_topic_searcher
from altaircms.models import Genre
from altaircms.topic.models import TopcontentTag

@view_config(route_name='home', renderer='cmsmobile:templates/top/top.mako')
def main(request):

    searcher = get_topic_searcher(request,  "topcontent")



    genre = Genre.query.filter_by()
    #genre = Performance.query.filter_by(label=u"音楽")
    #tag = TopcontentTag.query.filter_by(label=u"注目のイベント")
    #qs = searcher.query_publishing_topics(datetime.now(), tag=tag,  genre=genre)


    #   print(qs)
    return {
        }
