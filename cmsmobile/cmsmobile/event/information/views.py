# -*- coding: utf-8 -*-

from pyramid.view import view_config
from altaircms.topic.models import TopicTag
from datetime import datetime
from altaircms.topic.api import get_topic_searcher
from cmsmobile.event.information.forms import InformationForm

class ValidationFailure(Exception):
    pass

@view_config(route_name='information', renderer='cmsmobile:templates/information/information.mako')
@view_config(route_name='infodetail', renderer='cmsmobile:templates/information/infodetail.mako')
def move_information(request):

    form = InformationForm()

    #公演中止情報
    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"公演中止情報").first()
    if tag is not None:
        form.informations.data = topic_searcher.query_publishing_topics(datetime.now(), tag).all()

    return {'form':form}
