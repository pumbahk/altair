# -*- coding:utf-8 -*-
from datetime import datetime

from altair.app.ticketing.events.forms import EventForm
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

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
    getter = PrintProgressGetter(request, context.organization)
    print_progress_form = PrintProgressForm(request.POST, performance_ids=context.performance_id_list)
    progress = getter.get_event_progress(
        event
        , print_progress_form.product_item_id.data
        , print_progress_form.start_on.data
        , print_progress_form.end_on.data
    )
    return dict(
        event=event,
        printed_report_setting=context.printed_report_setting,
        form=EventForm(context=context),
        progress=progress,
        print_progress_form=print_progress_form
    )


@view_config(route_name="performances.print_progress.show", permission="authenticated",
             renderer='altair.app.ticketing:templates/performances/show.html',
             decorator="altair.app.ticketing.fanstatic.with_bootstrap")
def show_performance_print_progress(context, request):
    performance = context.target
    if performance is None:
        raise HTTPNotFound("performance is not found. (performance_id={})".format(context.performance_id))
    getter = PrintProgressGetter(request, context.organization)
    print_progress_form = PrintProgressForm(request.POST, performance_ids=[context.performance_id])
    progress = getter.get_performance_progress(
        performance
        , print_progress_form.product_item_id.data
        , print_progress_form.start_on.data
        , print_progress_form.end_on.data
    )

    return dict(
        tab="print_progress",
        performance=performance,
        progress=progress,
        print_progress_form=print_progress_form,
    )


@view_config(route_name="events.print_progress.easy_show",
             renderer="altair.app.ticketing:templates/events/easy_print_progress.html",
             decorator="altair.app.ticketing.fanstatic.with_bootstrap")
def show_event_print_progress_easy(context, request):
    event = context.target
    if event is None:
        raise HTTPNotFound("event is not found. (event_id={})".format(context.event_id))
    getter = PrintProgressGetter(request, context.organization)
    now = datetime.now()

    # 当日分固定
    progress = getter.get_event_progress_easy(
        event
        , None
        , datetime.strptime("{0.year}-{0.month}-{0.day} 00:00:00".format(now), '%Y-%m-%d %H:%M:%S')
        , datetime.strptime("{0.year}-{0.month}-{0.day} 23:59:59".format(now), '%Y-%m-%d %H:%M:%S')
    )
    return dict(
        event=event,
        printed_report_setting=context.printed_report_setting,
        progress=progress,
    )


@view_config(route_name="performances.print_progress.easy_show",
             renderer='altair.app.ticketing:templates/performances/easy_show.html',
             decorator="altair.app.ticketing.fanstatic.with_bootstrap")
def show_performance_print_progress_easy(context, request):
    performance = context.target
    if performance is None:
        raise HTTPNotFound("performance is not found. (performance_id={})".format(context.performance_id))
    getter = PrintProgressGetter(request, context.organization)
    print_progress_form = PrintProgressForm(request.POST, performance_ids=[context.performance_id])
    progress = getter.get_performance_progress(
        performance
        , print_progress_form.product_item_id.data
        , print_progress_form.start_on.data
        , print_progress_form.end_on.data
    )

    return dict(
        tab="print_progress",
        performance=performance,
        progress=progress,
        print_progress_form=print_progress_form,
    )
