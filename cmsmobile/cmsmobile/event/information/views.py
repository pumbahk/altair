# -*- coding: utf-8 -*-

from pyramid.view import view_config
from altaircms.topic.models import TopicTag
from datetime import datetime
from altaircms.topic.api import get_topic_searcher

class ValidationFailure(Exception):
    pass

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
