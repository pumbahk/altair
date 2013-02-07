# coding: utf-8
def includeme(config):
    config.add_route("promotion_list", "/promotion/list", factory=".resources.PromotionPageContext")
    config.add_route("promotion_detail", "/promotion/page/{page_id}/detail", factory=".resources.PromotionPageContext") #_query=dict(widget_id=widget_id)

    config.add_route("topcontent_list", "/topcontent/list", factory=".resources.TopcontentPageContext")
    config.add_route("topcontent_detail", "/topcontent/page/{page_id}/detail", factory=".resources.TopcontentPageContext") #_query=dict(widget_id=widget_id)

    config.add_route("api_promotion_addtag", "/api/promotion/tag/add",factory=".resources.PromotionTagContext")
    config.add_route("api_topcontent_addtag", "/api/topcontent/tag/add", factory=".resources.TopcontentTagContext")
    config.add_view("..tag.views.PublicTagCreateView", route_name="api_promotion_addtag", 
                    attr="create", request_method="POST", renderer="json")
    config.add_view("..tag.views.PublicTagCreateView", route_name="api_topcontent_addtag", 
                    attr="create", request_method="POST", renderer="json")

    config.scan(".views")
