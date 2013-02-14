# -*- coding:utf-8 -*-
def includeme(config):
    config.add_crud("layout", title="layout", model="..layout.models.Layout",
                    bind_actions=["delete"], 
                    form=".forms.LayoutCreateForm", mapper=".mappers.layout_mapper")
    config.add_crud("performance", title="performance", model="..models.Performance",
                    bind_actions=["create", "delete", "update"], 
                    form=".forms.PerformanceForm", mapper=".mappers.performance_mapper")

    config.add_view(".views.performance_detail", match_param="action=detail", permission="performance_update", 
                    route_name="performance_update", 
                    decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
                    renderer="altaircms:templates/performance/view.html")

    config.add_crud("sale", title="sale", model="..models.Salessegment", 
                    bind_actions=["create", "delete", "update"], 
                    form=".forms.SalessegmentForm", mapper=".mappers.sale_mapper")
    config.add_crud("ticket", title="ticket", model="..models.Ticket", 
                    bind_actions=["create", "delete", "update"], 
                    form=".forms.TicketForm", mapper=".mappers.ticket_mapper")


    ## topic
    config.add_crud("topic_unit", title="topic", model="..topic.models.Topic",
                    has_auto_generated_permission=False,  #todo:remove-it
                    form=".forms.TopicForm", mapper=".mappers.topic_mapper", 
                    events=dict(create_event=config.maybe_dotted(".subscribers.TopicCreate"), 
                                update_event=config.maybe_dotted(".subscribers.TopicUpdate"), 
                                ))

    config.add_crud("topcontent_unit", title="topcontent", model="..topic.models.Topcontent",
                    has_auto_generated_permission=False,  #todo:remove-it
                    form=".forms.TopcontentForm", mapper=".mappers.topcontent_mapper", 
                    events=dict(create_event=config.maybe_dotted(".subscribers.TopicCreate"), 
                                update_event=config.maybe_dotted(".subscribers.TopicUpdate"), 
                                ))
    config.add_crud("promotion_unit",  title="promotion",  model="..topic.models.Promotion",
                    has_auto_generated_permission=False,  #todo:remove-it
                    form=".forms.PromotionForm", mapper=".mappers.promotion_mapper", 
                    events=dict(create_event=config.maybe_dotted(".subscribers.TopicCreate"), 
                                update_event=config.maybe_dotted(".subscribers.TopicUpdate"), 
                                ))
    config.add_subscriber(".subscribers.update_kind", ".subscribers.TopicCreate")
    config.add_subscriber(".subscribers.update_kind", ".subscribers.TopicUpdate")

    config.add_crud("category", title="category", model="..models.Category",
                    bind_actions=["delete", "update", "create"], 
                    form=".forms.CategoryForm", mapper=".mappers.category_mapper", 
                    filter_form=".forms.CategoryFilterForm")
    config.add_route("category_list", "/category")
    config.add_view(".views.category_list_view", route_name="category_list", permission="category_read", 
                    decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
                    renderer="altaircms:templates/category/list.html")
    config.add_crud("category.link", title="external link", model="..models.Category",
                    has_auto_generated_permission=False, 
                    bind_actions=["create", "update"], 
                    endpoint="category_list", 
                    form=".forms.ExternalLinkForm", mapper=".mappers.category_mapper")
    config.add_crud("category.banner", title="external banner", model="..models.Category",
                    has_auto_generated_permission=False, 
                    bind_actions=["create", "update"], 
                    endpoint="category_list", 
                    form=".forms.ExternalBannerForm", mapper=".mappers.category_mapper")
    config.add_crud("hotword", title="hotword", model="..tag.models.HotWord",
                    form=".forms.HotWordForm", mapper=".mappers.hotword_mapper")
    config.add_crud("pagedefaultinfo", title="pagedefaultinfo", model="..page.models.PageDefaultInfo",
                    bind_actions=["create", "delete", "update"], 
                    form=".forms.PageDefaultInfoForm", mapper=".mappers.pagedefaultinfo_mapper")


"""
memo:
performance, ticket, sale, pagedefaultinfoはorganization_idを持っていない。
これは、cmsサイト上に一覧画面を表示しないことを表している。
(一覧が必要なら、organization_idを追加する)
"""
