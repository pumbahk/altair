# -*- coding:utf-8 -*-
import functools
from pyramid.path import AssetResolver
from wtforms.validators  import ValidationError

__all__ = ["ValidationError", "SESSION_NAME", "includeme"]
SESSION_NAME = "asset"
PROXY_FACTORY_NAME = "asset"

def _make_asset_filesession(assetspec):
    from ..filelib import FileSession
    from ..filelib.core import on_file_exists_try_rename
    savepath = AssetResolver().resolve(assetspec).abspath()
    filesession = FileSession(make_path=lambda : savepath, 
                              on_file_exists=on_file_exists_try_rename)
    filesession.assetspec = assetspec
    return filesession

def install_virtual_asset(config):
    from ..modelmanager.virtualasset import VirtualAssetFactory
    from ..modelmanager.interfaces import IRenderingObjectFactory
    provided = VirtualAssetFactory(static_route_name="__staticasset/")
    config.registry.registerUtility(provided, IRenderingObjectFactory, name=PROXY_FACTORY_NAME)
    assert config.registry.queryUtility(IRenderingObjectFactory, name=PROXY_FACTORY_NAME)



def includeme(config):
    """
    altaircms.asset.storepath = altaircms:../../data/assets
    """
    settings = config.registry.settings
    ## file session
    filesession = _make_asset_filesession(settings["altaircms.asset.storepath"])
    config.add_filesession(filesession, name=SESSION_NAME)

    ## virtual asset
    config.include(install_virtual_asset)

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
