# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('search', '/search')
    config.add_route('mobile_tag_search', '/search/{mobile_tag_id}/{genre}/{sub_genre}/{page}')
    config.add_route('genresearch', '/genresearch')
