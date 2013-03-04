# -*- coding: utf-8 -*-

from pyramid.view import view_config
from altaircms.topic.models import TopicTag
from datetime import datetime
from altaircms.topic.api import get_topic_searcher

class ValidationFailure(Exception):
    pass

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
