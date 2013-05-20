# coding: utf-8

def install_resolver(config):
    settings = config.registry.settings
    from altairsite.front.impl import LayoutModelResolver
    from altairsite.front.impl import ILayoutModelResolver
    layout_lookup = LayoutModelResolver(settings["altaircms.layout_directory"], 
                                   checkskip=True)
    config.registry.registerUtility(layout_lookup, ILayoutModelResolver)

def install_fetcher(config):
    settings = config.registry.settings
    from altairsite.front.fetcher import ICurrentPageFetcher
    from altairsite.front.fetcher import CurrentPageFetcher
    fetcher = CurrentPageFetcher(settings["altaircms.static.pagetype.pc"], 
                                 settings["altaircms.static.pagetype.mobile"])
    config.registry.registerUtility(fetcher, ICurrentPageFetcher)
    
def includeme(config):
    """
    templateの取得に必要なsettings
    altaircms.layout_directory: ここに指定されたpathからレイアウトのテンプレートを探す
    """
    config.add_route('front', '{page_name:.*}', factory=".resources.PageRenderingResource")
    config.include(install_resolver)
    config.include(install_fetcher)
    config.scan('.views')
