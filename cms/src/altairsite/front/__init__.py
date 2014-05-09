# coding: utf-8

def install_resolver(config):
    settings = config.registry.settings
    from altairsite.front.resolver import LayoutModelResolver
    from altairsite.front.resolver import ILayoutModelResolver
    layout_lookup = LayoutModelResolver(settings["altaircms.layout_directory"], 
                                   checkskip=True)
    config.registry.registerUtility(layout_lookup, ILayoutModelResolver)

def install_lookupwrapper(config, name="intercept", usersite=True):
    from beaker.cache import cache_regions #xxx:
    from pyramid.mako_templating import IMakoLookup
    from altairsite.front.renderer import (
        ILookupWrapperFactory,
        CmsLayoutModelLookupWrapperFactory,
        UsersiteLayoutModelLookupWrapperFactory,
        S3Loader,
        FileCacheLoader,
        CompositeLoader
    )
    settings = config.registry.settings
    #assert cache_regions["altaircms.layout.filedata"]["expire"] == 5724000
    loader = CompositeLoader(FileCacheLoader(cache_regions["altaircms.layout.filedata"],
                                             cache_regions["altaircms.fetching.filedata"]),
                             S3Loader(bucket_name=settings["s3.bucket_name"],
                                      access_key=settings["s3.access_key"],
                                      secret_key=settings["s3.secret_key"],))

    factory = CmsLayoutModelLookupWrapperFactory(directory_spec=settings["altaircms.layout_directory"],
                                              loader=loader,
                                              prefix=settings["altaircms.layout_s3prefix"])
    if usersite:
        factory = UsersiteLayoutModelLookupWrapperFactory(directory_spec=settings["altaircms.layout_directory"],
                                                  loader=loader,
                                                  prefix=settings["altaircms.layout_s3prefix"])


    config.registry.adapters.register([IMakoLookup], ILookupWrapperFactory, name=name, value=factory)


def install_usersite_lookupwrapper(config, name="intercept"):
    install_lookupwrapper(config, name, True)

def install_cms_lookupwrapper(config, name="intercept"):
    install_lookupwrapper(config, name, False)

def install_page_key_generator(config):
    from altair.mobile.interfaces import ISmartphoneRequest
    from altair.mobile.interfaces import IMobileRequest
    from pyramid.interfaces import IRequest
    from .cache import (
        ICacheKeyGenerator, 
        CacheKeyGenerator, 
    )
    config.registry.adapters.register([ISmartphoneRequest], ICacheKeyGenerator, "", CacheKeyGenerator("S:"))
    config.registry.adapters.register([IMobileRequest], ICacheKeyGenerator, "", CacheKeyGenerator("M:"))
    config.registry.adapters.register([IRequest], ICacheKeyGenerator, "", CacheKeyGenerator("P:"))

def install_pagecache(config):
    from beaker.cache import cache_regions #xxx:
    from .cache import (
        IFrontPageCache,
        FileCacheStore,
        WrappedFrontPageCache,
        update_browser_id,
        ICacheTweensSetting
    )
    fetching_kwargs = cache_regions["altaircms.fetching.filedata"]
    kwargs = cache_regions["altaircms.frontpage.filedata"]
    front_page_cache = WrappedFrontPageCache(FileCacheStore(kwargs), update_browser_id)
    config.registry.registerUtility(front_page_cache, IFrontPageCache)
    tween_settings = {"expire": kwargs["expire"], "kwargs": fetching_kwargs}
    config.registry.registerUtility(tween_settings, ICacheTweensSetting)

def includeme(config):
    """
    templateの取得に必要なsettings
    altaircms.layout_directory: ここに指定されたpathからレイアウトのテンプレートを探す
    """
    config.add_route('front', '{page_name:.*}', factory=".resources.PageRenderingResource")
    config.include(install_resolver)
    config.include(install_usersite_lookupwrapper)
    config.include(install_pagecache)
    config.include(install_page_key_generator)
    config.add_tween('altairsite.front.cache.cached_view_tween', under='altair.preview.tweens.preview_tween')
    config.scan('.views')
    from .views import not_static_path
    config.add_view("altairsite.mobile.staticpage.views.staticpage_view", route_name="front", request_type="altairsite.tweens.IMobileRequest", custom_predicates=(not_static_path, ))

