# -*- coding:utf-8 -*-
from functools import partial


def includeme(config):

    add_p_route = partial(config.add_route, factory=".resources.LiveStreamingResource")
    add_p_route("performances.live_streaming.show", "/events/performances/live_streaming/{performance_id}")
    config.scan(".views")
