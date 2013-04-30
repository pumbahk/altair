# coding: utf-8

def includeme(config):
    """
    templateの取得に必要なsettings
    altaircms.layout_directory: ここに指定されたpathからレイアウトのテンプレートを探す
    """
    settings = config.registry.settings
    from altairsite.front.impl import LayoutTemplate
    from altairsite.front.impl import ILayoutTemplateLookUp
    layout_lookup = LayoutTemplate(settings["altaircms.layout_directory"], 
                                   checkskip=True)
    config.registry.registerUtility(layout_lookup, ILayoutTemplateLookUp)
    config.add_route('front', '{page_name:.*}', factory=".resources.PageRenderingResource")
    config.scan('.views')
