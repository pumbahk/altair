# -*- coding:utf-8 -*-
from functools import partial


def includeme(config):
    add_p_route = partial(config.add_route, factory=".resources.LiveStreamingResource")
    add_p_route("performances.live_streaming.edit", "/events/performances/live_streaming/edit/{performance_id}")
    config.scan(".views")
