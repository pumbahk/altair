# -*- coding:utf-8 -*-
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated

from altair.app.ticketing.events.forms import EventForm
from .forms import PrintProgressForm
from .progress import PrintProgressGetter

##TODO:edit permission
@view_config(route_name="events.print_progress.show", permission="authenticated", 
             renderer="altair.app.ticketing:templates/events/print_progress.html", 
             decorator="altair.app.ticketing.fanstatic.with_bootstrap")
def show_event_print_progress(context, request):
    event = context.target
    if event is None:
        raise HTTPNotFound("event is not found. (event_id={})".format(context.event_id))
    product_item_id = request.POST.get('product_item_id')
    getter = PrintProgressGetter(request, context.organization, product_item_id)
    progress = getter.get_event_progress(event)
    print_progress_form=PrintProgressForm(performance_ids=progress.performance_id_list)
    print_progress_form.product_item_id.data = product_item_id
    return dict(
        event=event,
        form=EventForm(context=context),
        print_progress_form=print_progress_form,
        progress=progress
    )

@view_config(route_name="performances.print_progress.show", permission="authenticated", 
             renderer='altair.app.ticketing:templates/performances/show.html', 
             decorator="altair.app.ticketing.fanstatic.with_bootstrap")
def show_performance_print_progress(context, request):
    performance = context.target
    if performance is None:
        raise HTTPNotFound("performance is not found. (performance_id={})".format(context.performance_id))
    product_item_id = request.POST.get('product_item_id')
    getter = PrintProgressGetter(request, context.organization, product_item_id)
    progress = getter.get_performance_progress(performance)
    print_progress_form=PrintProgressForm(performance_ids=progress.performance_id_list)
    print_progress_form.product_item_id.data = product_item_id
    return dict(
        tab="print_progress", 
        performance=performance,
        progress=progress,
        print_progress_form=print_progress_form,
    )

