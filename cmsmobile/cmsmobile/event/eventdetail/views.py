# -*- coding: utf-8 -*-
from pyramid.view import view_config
from altaircms.event.models import Event
from cmsmobile.event.eventdetail.forms import EventDetailForm
from cmsmobile.core.helper import get_week_map, get_performances_month_unit, get_purchase_links

class ValidationFailure(Exception):
    pass

@view_config(route_name='eventdetail', renderer='cmsmobile:templates/eventdetail/eventdetail.mako')
def move_eventdetail(request):
    form = EventDetailForm(request.GET)
    form.week.data = get_week_map()
    form.event.data = request.allowable(Event).filter(Event.id == form.event_id.data).first()

    if not form.event.data:
        raise ValidationFailure

    form.purchase_links.data = get_purchase_links(request=request, event=form.event.data)
    form.month_unit.data = get_performances_month_unit(event=form.event.data)
    keys = form.month_unit.data.keys()
    keys.sort()
    form.month_unit_keys.data = keys
    return {'form':form}

@view_config(route_name='eventdetail', context=ValidationFailure, renderer='cmsmobile:templates/common/error.mako')
def failed_validation(request):
    return {}
