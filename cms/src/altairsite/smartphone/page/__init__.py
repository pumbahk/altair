# -*- coding: utf-8 -*-
import functools

def includeme(config):
    add_route = functools.partial(config.add_route, factory="altairsite.smartphone.page.resources.PageResource")
    add_route('page', '/page/{kind}')
