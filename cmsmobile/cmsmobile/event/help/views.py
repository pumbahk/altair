# -*- coding: utf-8 -*-

from pyramid.view import view_config
from altaircms.topic.models import TopicTag
from datetime import datetime
from altaircms.topic.api import get_topic_searcher
from cmsmobile.event.help.forms import HelpForm

class ValidationFailure(Exception):
    pass

@view_config(route_name='help', renderer='cmsmobile:templates/help/help.mako')
def move_help(request):

    form = HelpForm()

    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"質問").first()

    if tag is not None:
        form.helps.data = topic_searcher.query_publishing_topics(datetime.now(), tag).all()

    return {'form':form}
