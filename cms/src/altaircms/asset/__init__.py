# -*- coding:utf-8 -*-

import functools
def includeme(config):
    add_route = functools.partial(config.add_route, factory=".resources.AssetResource")
    add_route("asset_add", "/asset/{kind}")

    add_route('asset_list', '')
    add_route("asset_image_list", "/image")
    add_route('asset_movie_list', '/movie')
    add_route('asset_flash_list', '/flash')

    add_route('asset_image_create', '/image/create')
    add_route('asset_movie_create', '/movie/create')
    add_route('asset_flash_create', '/flash/create')

    add_route("asset_search", '/search')
    add_route("asset_search_image", '/image/search')
    add_route("asset_search_movie", '/movie/search')
    add_route("asset_search_flash", '/flash/search')

    add_route('asset_image_delete', '/image/{asset_id}/delete')
    add_route('asset_movie_delete', '/movie/{asset_id}/delete')
    add_route('asset_flash_delete', '/flash/{asset_id}/delete')
    
    add_route('asset_display', '/display/{asset_id}')

    add_route('asset_image_detail', '/image/{asset_id}')
    add_route('asset_movie_detail', '/movie/{asset_id}')
    add_route('asset_flash_detail', '/flash/{asset_id}')
    add_route('asset_detail', '/{asset_type}/{asset_id}')

    add_route('asset_image_input', '/image/{asset_id}/input')
    add_route('asset_movie_input', '/movie/{asset_id}/input')
    add_route('asset_flash_input', '/flash/{asset_id}/input')

    add_route('asset_image_update', '/image/{asset_id}/update')
    add_route('asset_movie_update', '/movie/{asset_id}/update')
    add_route('asset_flash_update', '/flash/{asset_id}/update')

    config.scan()
