# -*- coding: utf-8 -*-
from pyramid.view import view_config
from altaircms.event.models import Event
from cmsmobile.event.eventdetail.forms import EventDetailForm
from cmsmobile.core.helper import get_week_map, get_performances_month_unit, get_purchase_links, get_tickets
from cmsmobile.core.helper import log_info

class ValidationFailure(Exception):
    pass

@view_config(route_name='eventdetail', renderer='cmsmobile:templates/eventdetail/eventdetail.mako')
def move_eventdetail(request):

    log_info("move_eventdetail", "start")
    form = EventDetailForm(request.GET)
    form.week.data = get_week_map()
    form.event.data = request.allowable(Event).filter(Event.id == form.event_id.data).first()

    if not form.event.data:
        log_info("move_eventdetail", "event not found")
        raise ValidationFailure

    log_info("move_eventdetail", "detail infomation get start")
    form.purchase_links.data = get_purchase_links(request=request, event=form.event.data)
    form.month_unit.data = get_performances_month_unit(event=form.event.data)
    keys = form.month_unit.data.keys()
    keys.sort()
    form.month_unit_keys.data = keys
    form.tickets.data = get_tickets(form.event.data)
    log_info("move_eventdetail", "detail infomation get end")

    log_info("move_eventdetail", "end")
    return {'form':form}

@view_config(route_name='eventdetail', context=ValidationFailure, renderer='cmsmobile:templates/common/error.mako')
def failed_validation(request):
    return {}
