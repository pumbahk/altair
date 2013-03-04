# -*- coding: utf-8 -*-

from pyramid.view import view_config
from datetime import datetime
from altaircms.topic.api import get_topic_searcher
from cmsmobile.event.hotword.forms import HotwordForm
from altaircms.tag.models import HotWord

class ValidationFailure(Exception):
    pass

@view_config(route_name='hotword', context=ValidationFailure, renderer='cmsmobile:templates/common/error.mako')
def failed_validation(request):
    return {}

@view_config(route_name='hotword', renderer='cmsmobile:templates/hotword/hotword.mako')
def move_hotword(request):

    form = HotwordForm(request.GET)

    if form.id.data == "" or form.id.data is None:
        raise ValidationFailure

    hotword = HotWord.query.filter(HotWord.id == form.id.data).first()

    if hotword is not None:
        searcher = get_topic_searcher(request, "topic")
        event = searcher.query_publishing_topics(datetime.now(), hotword.tag) \
                     .filter(hotword.tag.organization_id == request.organization.id).first()

    """
    ココらへんは動かないのであとで修正する。
    """
    if not event:
        raise ValidationFailure

    return {
        'events':[event]
    }
