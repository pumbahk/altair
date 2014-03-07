# -*- coding:utf-8 -*-
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated

from altair.app.ticketing.events.forms import EventForm
#from altair.app.ticketing.core.progress import PrintProgressGetter

from collections import namedtuple
ProgressData = namedtuple("ProgressData", "total printed unprinted")
from pyramid.decorator import reify
from altair.app.ticketing.core.models import Event, Performance




class PrintProgressGetter(object):
    def __init__(self, request, organization):
        self.request = request
        self.organization = organization

    def get_progress_information(self, target):
        ##todo: adapter or anything.
        return DummyPrintProgress()
        if isinstance(target, Event):
            pass
        elif isinstance(target, Performance):
            pass

class DummyPrintProgress(object):
    @reify
    def total(self):
        return 300

    @property
    def size(self):
        return 3

    @reify
    def qr(self):
        return ProgressData(total=100, printed=40, unprinted=60)

    @reify
    def shipping(self):
        return ProgressData(total=100, printed=100, unprinted=0)

    @reify
    def other(self):
        return ProgressData(total=20, printed=19, unprinted=1)

##TODO:edit permission
@view_config(route_name="events.print_progress.show", permission="authenticated", 
             renderer="altair.app.ticketing:templates/events/print_progress.html", 
             decorator="altair.app.ticketing.fanstatic.with_bootstrap")
def show_progress(context, request):
    event = context.target
    if event is None:
        raise HTTPNotFound("event is not found. (event_id={})".format(context.event_id))

    getter = PrintProgressGetter(request, context.organization)
    progress = getter.get_progress_information(event)
    return dict(
        event=event,
        form=EventForm(),
        progress=progress
    )
