# -*- coding:utf-8 -*-
from functools import partial

def includeme(config):
    add_route = partial(config.add_route, factory=".resources.EventPrintProgressResource")
    add_route("events.print_progress.show", "/{event_id}")

