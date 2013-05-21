# -*- coding:utf-8 -*-
SESSION_NAME = "staticupload"
from pyramid.path import AssetResolver

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

def includeme(config):
    from .api import set_static_page_utility
    config.add_route("static_pageset", "/page/pagetype/{pagetype}/{static_page_id}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page_create", "/page/pagetype/{pagetype}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page", "/page/static/{static_page_id}/unit/{child_id}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page_display", "/page/static/display/{path:.*}",factory=".resources.StaticPageResource")
    settings = config.registry.settings
    set_static_page_utility(
        config, 
        settings["altaircms.page.static.directory"], 
        settings["altaircms.page.tmp.directory"]
        )

    config.add_route("static_page_part_file", "/page/static/{static_page_id}/unit/{child_id}/file/{path}/{action}", factory=".resources.StaticPageResource")
    config.add_route("static_page_part_directory", "/page/static/{static_page_id}/unit/{child_id}/file/{path}/{action}", factory=".resources.StaticPageResource")

    config.add_subscriber(".subscribers.delete_ignorefile_after_staticupload", ".directory_resources.AfterCreate")
    config.add_subscriber(".subscribers.refine_html_files_after_staticupload", ".directory_resources.AfterCreate")
    config.scan(".views")

