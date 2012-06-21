# coding: utf-8

def includeme(config):
    config.add_route('front', '/publish/{page_name:.*}', factory=".resources.PageRenderingResource") # fix-url after. implemnt preview
    config.add_route("front_to_preview", "/to/preview/{page_id}", factory=".resources.PageRenderingResource")
    config.add_route('front_preview', '/{page_id}/preview/{page_name:.*}', factory=".resources.PageRenderingResource")

    ## mobile
    config.add_view("altairsite.mobile.views.mobile_index",
                    route_name="front",
                    renderer="altaircms:templates/mobile/index.mako", 
                    context="altairsite.mobile.api.MobileGotoTop")
    config.add_view("altairsite.mobile.views.mobile_category",
                    route_name="front",
                    renderer="altaircms:templates/mobile/category.mako", 
                    context="altairsite.mobile.api.MobileGotoCategoryTop")
    config.add_view("altairsite.mobile.views.mobile_detail",
                    route_name="front",
                    renderer="altaircms:templates/mobile/detail.mako", 
                    context="altairsite.mobile.api.MobileGotoEventDetail")
    config.add_view("altairsite.mobile.views.mobile_semi_static",
                    route_name="front",
                    context="altairsite.mobile.api.MobileGotoStatic")

    config.scan('.views')
