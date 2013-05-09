# -*- coding: utf-8 -*-
import functools

def includeme(config):
    add_route = functools.partial(config.add_route, factory="altairsite.smartphone.event.detail.resources.DetailPageResource")
    add_route('detail', '/detail')
