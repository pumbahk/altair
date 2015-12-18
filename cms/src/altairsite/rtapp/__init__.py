# -*- coding:utf-8 -*-

def includeme(config):
    config.add_route('api.top_page', '/app-api/top')
    config.add_route('api.genre_list', '/app-api/genres')
    config.add_route('api.performance_list', '/app-api/performances')
    config.add_route('api.event_detail', '/app-api/event/{event_id}')
    config.add_route('api.bookmark_events', '/app-api/bookmark/events')
    config.scan(".views")
