# -*- coding:utf-8 -*-
import functools
from pyramid.path import AssetResolver
from wtforms.validators  import ValidationError

__all__ = ["ValidationError", "SESSION_NAME", "includeme"]
SESSION_NAME = "asset"
PROXY_FACTORY_NAME = "asset"


def install_virtual_asset(config):
    from ..modelmanager.virtualasset import VirtualAssetFactory
    from ..modelmanager.interfaces import IRenderingObjectFactory
    provided = VirtualAssetFactory(static_route_name="__staticasset/")
    config.registry.registerUtility(provided, IRenderingObjectFactory, name=PROXY_FACTORY_NAME)
    assert config.registry.queryUtility(IRenderingObjectFactory, name=PROXY_FACTORY_NAME)

def install_filesession(config):
    from ..filelib.core import on_file_exists_try_rename
    settings = config.registry.settings

    ## filesession
    FileSession = config.maybe_dotted(settings["altaircms.filesession"])
    assetspec = settings["altaircms.asset.storepath"]
    savepath = AssetResolver().resolve(assetspec).abspath()
    filesession = FileSession(make_path=lambda : savepath, 
                              on_file_exists=on_file_exists_try_rename, 
                              marker=SESSION_NAME, 
                              options={"public": True})
    filesession.assetspec = assetspec
    config.add_filesession(filesession, name=SESSION_NAME)

def install_s3sync(config):
    ## s3 upload setting
    ## after s3 upload event
    ## file upload -> s3 upload -> set file url
    config.add_subscriber(".subscribers.rename_for_s3_upload", "altaircms.filelib.s3.BeforeS3Upload")
    config.add_subscriber(".subscribers.set_file_url", "altaircms.filelib.s3.AfterS3Upload")
    config.add_subscriber(".subscribers.unpublish_deleted_files_on_s3", "altaircms.filelib.s3.AfterS3Delete")
    
def includeme(config):
    """
    altaircms.asset.storepath = altaircms:../../data/assets
    """
    config.include(install_filesession)
    config.include(install_s3sync)
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
