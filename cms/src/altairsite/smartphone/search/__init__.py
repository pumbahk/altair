# -*- coding: utf-8 -*-
import functools

def includeme(config):
    add_route = functools.partial(config.add_route, factory="altairsite.smartphone.search.resources.SearchPageResource")
    add_route('smartphone.search', '/search')
    add_route('smartphone.search_area', '/search_area')
    add_route('smartphone.search_genre', '/search_genre')
    add_route('smartphone.search_genre_area', '/search_genre_area')
    add_route('smartphone.init_detail', '/init_detail')
    add_route('smartphone.search_detail', '/search_detail')
    add_route('smartphone.search_subsubgenre', '/subgenre')
    add_route('smartphone.hotword', '/hotword')
