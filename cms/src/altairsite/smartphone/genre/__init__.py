# -*- coding: utf-8 -*-
import functools

def includeme(config):
    add_route = functools.partial(config.add_route, factory="altairsite.smartphone.genre.resources.GenrePageResource")
    add_route('genre', '/genre/{genre_id}')
