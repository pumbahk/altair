# -*- coding:utf-8 -*-
from functools import partial

def includeme(config):
    add_e_route = partial(config.add_route, factory=".resources.EventPrintProgressResource")
    add_e_route("events.print_progress.show", "/events/print_progress/{event_id}")

    add_p_route = partial(config.add_route, factory=".resources.PerformancePrintProgressResource")
    add_p_route("performances.print_progress.show", "/events/performances/print_progress/{performance_id}")
    config.scan(".views")
