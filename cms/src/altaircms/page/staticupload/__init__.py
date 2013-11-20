# -*- coding:utf-8 -*-
SESSION_NAME = "staticupload"
from pyramid.path import AssetResolver

import logging
logger = logging.getLogger(__name__)

class StaticUploadAssertionError(Exception):
    pass

def is_html_filename(filename):
    return filename.lower().endswith((".html", ".htm"))

def validate_uploaded_file(filename, output):
    try:
        output.decode("utf-8")
    except UnicodeDecodeError as e:
        logger.warn("unicode decode error: filename {}: error({})".format(filename, repr(e)))
        raise StaticUploadAssertionError(u"以下のファイルが壊れている。あるいはエンコーディングがutf-8ではありません。 ファイル:{}".format(filename))

def validate_uploaded_io(filename, io):
    if not is_html_filename(filename):
        return
    validate_uploaded_file(filename, io.read()) #xxx:
    io.seek(0)

def install_static_page_cache(config):
    from .fetcher import StaticPageCache
    from .interfaces import IStaticPageCache
    from beaker.cache import cache_regions #xxx:
    k = "altaircms.staticpage.filedata"
    fetching_k = "altaircms.fetching.filedata"
    try:
        kwargs = cache_regions[k]
        fetching_kwargs = cache_regions[fetching_k]
        config.registry.registerUtility(StaticPageCache(kwargs, fetching_kwargs), IStaticPageCache)
    except KeyError:
        import sys
        sys.stderr.write("cache_regions[{k}] is not found\n".format(k=k))

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

def install_static_page_utility(config):
    from .api import set_static_page_utility
    settings = config.registry.settings
    FactoryClass = config.maybe_dotted(settings["altaircms.page.static.factoryclass"])
    set_static_page_utility(config, FactoryClass(settings["altaircms.page.static.directory"], 
                                                 tmpdir=settings["altaircms.page.tmp.directory"]))


def includeme(config):
    config.add_route("static_pageset", "/page/pagetype/{pagetype}/{static_page_id}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page_create", "/page/pagetype/{pagetype}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page", "/page/static/{static_page_id}/unit/{child_id}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page_display", "/page/static/{static_page_id}/unit/{child_id}/display/{path:.*}",factory=".resources.StaticPageResource")
    config.add_route("static_page_part_file", "/page/static/{static_page_id}/unit/{child_id}/file/{action}{path:.*}", factory=".resources.StaticPageResource")
    config.add_route("static_page_part_directory", "/page/static/{static_page_id}/unit/{child_id}/directory/{action}{path:.*}", factory=".resources.StaticPageResource")

    ## this is first..
    config.add_subscriber(".subscribers.delete_ignorefile_after_staticupload", ".directory_resources.AfterCreate")
    config.include(install_static_page_utility)
    config.include(install_static_page_cache)
    config.scan(".views")

