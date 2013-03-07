# -*- coding: utf-8 -*-
from pyramid.view import view_config
from altaircms.event.models import Event
from cmsmobile.event.eventdetail.forms import EventDetailForm

class ValidationFailure(Exception):
    pass

@view_config(route_name='eventdetail', renderer='cmsmobile:templates/eventdetail/eventdetail.mako')
def move_eventdetail(request):

    form = EventDetailForm(request.GET)
    form.event.data = request.allowable(Event).filter(Event.id == form.event_id.data).first()
    form.week.data = {0:u'月',1:u'火',2:u'水',3:u'木',4:u'金',5:u'土',6:u'日'}

    if not form.event.data:
        raise ValidationFailure

    return {
        'form':form
    }

@view_config(route_name='eventdetail', context=ValidationFailure, renderer='cmsmobile:templates/common/error.mako')
def failed_validation(request):
    return {}
