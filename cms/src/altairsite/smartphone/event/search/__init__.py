# -*- coding: utf-8 -*-
import functools

def includeme(config):
    add_route = functools.partial(config.add_route, factory="altairsite.smartphone.event.search.resources.SearchPageResource")
    add_route('search', '/search')
    add_route('search_area', '/search_area')
    add_route('search_genre', '/search_genre')
    add_route('search_genre_area', '/search_genre_area')
    add_route('init_detail', '/init_detail')
    add_route('search_detail', '/search_detail')
