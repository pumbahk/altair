# coding: utf-8
def includeme(config):
    # バックエンドからの受取り用。
    # 認証方式が異なるため独立したインターフェースを設ける。
    # config.add_route('api_topic_register', '/api/topic/register')

    config.add_route("promotion_list", "/promotion/list", factory=".resources.PromotionPageContext")
    config.add_route("topcontent_list", "/topcontent/list", factory=".resources.TopcontentPageContext")

    config.add_route('api_topic_object', '/api/topic/{id}')
    config.add_route('api_topic', '/api/topic/')

    config.add_route("promotion_detail", "/promotion/page/{page_id}/detail") #_query=dict(widget_id=widget_id)
    config.add_route("topcontent_detail", "/topcontent/page/{page_id}/detail") #_query=dict(widget_id=widget_id)
    config.add_route("api_promotion_addtag", "/api/promotion/tag/add", 
                     factory=".resources.PromotionTagContext")
    config.add_route("api_topcontent_addtag", "/api/topcontent/tag/add", 
                     factory=".resources.TopcontentTagContext")
    config.add_view("..tag.views.PublicTagCreateView", route_name="api_promotion_addtag", 
                    attr="create", request_method="POST", renderer="json")
    config.scan(".views")
