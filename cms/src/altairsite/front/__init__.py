# coding: utf-8

def install_resolver(config):
    settings = config.registry.settings
    from altairsite.front.resolver import LayoutModelResolver
    from altairsite.front.resolver import ILayoutModelResolver
    layout_lookup = LayoutModelResolver(settings["altaircms.layout_directory"], 
                                   checkskip=True)
    config.registry.registerUtility(layout_lookup, ILayoutModelResolver)

   
def includeme(config):
    """
    templateの取得に必要なsettings
    altaircms.layout_directory: ここに指定されたpathからレイアウトのテンプレートを探す
    """
    config.add_route('front', '{page_name:.*}', factory=".resources.PageRenderingResource")
    config.include(install_resolver)
    config.scan('.views')
    config.add_view("altairsite.mobile.staticpage.views.staticpage_view", route_name="front", request_type="altairsite.tweens.IMobileRequest")

