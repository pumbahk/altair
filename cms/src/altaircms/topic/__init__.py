# coding: utf-8

import functools
from .interfaces import ITopicSearcher

def includeme(config):
    config.include(install_topic_page)
    config.include(install_topcontent_page)
    config.include(install_promotion_page)
    config.scan(".views")
    config.include(install_topic_searcher)

def install_topic_page(config):
    config.add_route("topic_unit_list", "/topic/unit/list", factory=".resources.TopicPageContext")
    config.add_route("topic_list", "/topic/list", factory=".resources.TopicPageContext")
    config.add_route("topic_tag_list", "/topic/tags", factory=".resources.TopicPageContext")
    config.add_route("topic_detail", "/topic/page/{page_id}/detail", factory=".resources.TopicPageContext") #_query=dict(widget_id=widget_id)
    config.add_route("api_topic_addtag", "/api/topic/tag/add", factory=".resources.TopicTagContext")
    config.add_view("..tag.views.PublicTagCreateView", route_name="api_topic_addtag", 
                    attr="create", request_method="POST", renderer="json")

def install_topcontent_page(config):
    config.add_route("topcontent_unit_list", "/topcontent/unit/list", factory=".resources.TopcontentPageContext")
    config.add_route("topcontent_list", "/topcontent/list", factory=".resources.TopcontentPageContext")
    config.add_route("topcontent_tag_list", "/topcontent/tags", factory=".resources.TopcontentPageContext")
    config.add_route("topcontent_detail", "/topcontent/page/{page_id}/detail", factory=".resources.TopcontentPageContext") #_query=dict(widget_id=widget_id)
    config.add_route("api_topcontent_addtag", "/api/topcontent/tag/add", factory=".resources.TopcontentTagContext")
    config.add_view("..tag.views.PublicTagCreateView", route_name="api_topcontent_addtag", 
                    attr="create", request_method="POST", renderer="json")

def install_promotion_page(config):
    config.add_route("promotion_unit_list", "/promotion/unit/list", factory=".resources.PromotionPageContext")
    config.add_route("promotion_list", "/promotion/list", factory=".resources.PromotionPageContext")
    config.add_route("promotion_tag_list", "/promotion/tags", factory=".resources.PromotionPageContext")
    config.add_route("promotion_detail", "/promotion/page/{page_id}/detail", factory=".resources.PromotionPageContext") #_query=dict(widget_id=widget_id)
    config.add_route("api_promotion_addtag", "/api/promotion/tag/add",factory=".resources.PromotionTagContext")
    config.add_view("..tag.views.PublicTagCreateView", route_name="api_promotion_addtag", 
                    attr="create", request_method="POST", renderer="json")

def install_topic_searcher(config):
    topic = config.maybe_dotted(".models.Topic")
    from .searcher import GlobalTopicSearcher
    config.registry.registerUtility(functools.partial(GlobalTopicSearcher, topic),
                                    ITopicSearcher, name=topic.type)
    topcontent = config.maybe_dotted(".models.Topcontent")
    config.registry.registerUtility(functools.partial(GlobalTopicSearcher, topcontent),
                                    ITopicSearcher, name=topcontent.type)
    promotion = config.maybe_dotted(".models.Promotion")
    config.registry.registerUtility(functools.partial(GlobalTopicSearcher, promotion),
                                    ITopicSearcher, name=promotion.type)
