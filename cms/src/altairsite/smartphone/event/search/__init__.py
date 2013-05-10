# -*- coding: utf-8 -*-
import functools

def includeme(config):
    add_route = functools.partial(config.add_route, factory="altairsite.smartphone.event.search.resources.SearchPageResource")
    add_route('search', '/search')
    add_route('search_area', '/search_area')
    add_route('genre_search', '/genre_search')
    add_route('detail_search', '/detail_search')
