# coding: utf-8


def install_mobile_view(config):
    config.add_view("altairsite.mobile.views.mobile_index",
                    route_name="front",
                    renderer="altaircms:templates/mobile/index.html", 
                    context="altairsite.mobile.api.MobileGotoTop")
    config.add_view("altairsite.mobile.views.mobile_category",
                    route_name="front",
                    renderer="altaircms:templates/mobile/category.html", 
                    context="altairsite.mobile.api.MobileGotoCategoryTop")
    config.add_view("altairsite.mobile.views.mobile_detail",
                    route_name="front",
                    renderer="altaircms:templates/mobile/detail.html", 
                    context="altairsite.mobile.api.MobileGotoEventDetail")
    config.add_view("altairsite.mobile.views.mobile_semi_static",
                    route_name="front",
                    context="altairsite.mobile.api.MobileGotoStatic")

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
    ## mobile
    config.include(install_mobile_view)
    config.scan('.views')
