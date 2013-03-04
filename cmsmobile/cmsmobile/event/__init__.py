# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('search', '/search')
    config.add_route('genre', '/genre')
    config.add_route('genresearch', '/genresearch')
    config.add_route('detailsearch', '/detailsearch')
    config.add_route('eventdetail', '/eventdetail')
    config.add_route('information', '/information')
    config.add_route('help', '/help')
    config.add_route('order', '/order')
    config.add_route('company', '/company')
    config.add_route('hotword', '/hotword')
