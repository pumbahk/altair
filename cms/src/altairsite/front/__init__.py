# coding: utf-8

def install_static_page(config):
    settings = config.registry.settings
    config.maybe_dotted("altaircms.page.api.set_static_page_utility")(
        config, 
        settings["altaircms.page.static.directory"], 
        settings["altaircms.page.tmp.directory"]
        )


def includeme(config):
    """
    templateの取得に必要なsettings
    altaircms.layout_directory: ここに指定されたpathからレイアウトのテンプレートを探す
    """
    settings = config.registry.settings
    layout_lookup_class = config.maybe_dotted(".impl.LayoutTemplate")
    layout_lookup = layout_lookup_class(settings["altaircms.layout_directory"])
    config.registry.registerUtility(layout_lookup, config.maybe_dotted(".impl.ILayoutTemplateLookUp"))
    config.add_route('front', '{page_name:.*}', factory=".resources.PageRenderingResource")
    config.include(install_static_page)
    config.scan('.views')

def install_mobile_app(config):
    
