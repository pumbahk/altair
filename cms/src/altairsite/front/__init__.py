# coding: utf-8

def install_resolver(config):
    settings = config.registry.settings
    from altairsite.front.resolver import LayoutModelResolver
    from altairsite.front.resolver import ILayoutModelResolver
    layout_lookup = LayoutModelResolver(settings["altaircms.layout_directory"], 
                                   checkskip=True)
    config.registry.registerUtility(layout_lookup, ILayoutModelResolver)

def install_lookupwrapper(config, name="intercept"):
    from pyramid.mako_templating import IMakoLookup
    from altairsite.front.renderer import ILookupWrapperFactory
    from altairsite.front.renderer import LayoutModelLookupWrapperFactory
    from altairsite.front.renderer import S3Loader
    settings = config.registry.settings
    factory = LayoutModelLookupWrapperFactory(directory_spec=settings["altaircms.layout_directory"], 
                                              loader=S3Loader(bucket_name=settings["s3.bucket_name"], 
                                                              access_key=settings["s3.access_key"],                                               
                                                              secret_key=settings["s3.secret_key"], 
                                                              ), 
                                              prefix=settings["altaircms.layout_s3prefix"])
    config.registry.adapters.register([IMakoLookup], ILookupWrapperFactory, name=name, value=factory)
   
def install_pagecache(config):
    from .cache import IFrontPageCache
    from .cache import FrontPageCacher
    from beaker.cache import cache_regions #xxx:
    kwargs = cache_regions["altaircms.frontpage.filedata"]
    cacher = FrontPageCacher(kwargs=kwargs)
    config.registry.registerUtility(cacher, IFrontPageCache)

def includeme(config):
    """
    templateの取得に必要なsettings
    altaircms.layout_directory: ここに指定されたpathからレイアウトのテンプレートを探す
    """
    config.add_route('front', '{page_name:.*}', factory=".resources.PageRenderingResource")
    config.include(install_resolver)
    config.include(install_lookupwrapper, "intercept")
    config.include(install_pagecache)
    config.scan('.views')
    from altairsite.front.cache import with_mobile_cache
    config.add_view("altairsite.mobile.staticpage.views.staticpage_view", route_name="front", request_type="altairsite.tweens.IMobileRequest", decorator=with_mobile_cache)

