# -*- coding:utf-8 -*-
def includeme(config):
    config.add_crud("layout", title="layout", model="..layout.models.Layout",
                    circle_type="circle-master", 
                    bind_actions=["delete"], 
                    form=".forms.LayoutCreateForm", mapper=".mappers.layout_mapper")
    config.add_crud("performance", title="performance", model="..models.Performance",
                    circle_type="circle-event", 
                    bind_actions=["create", "delete", "update"], 
                    events=dict(create_event=config.maybe_dotted(".subscribers.PerformanceCreate"), 
                                update_event=config.maybe_dotted(".subscribers.PerformanceUpdate"), 
                                ), 
                    form=".forms.PerformanceForm", mapper=".mappers.performance_mapper")
    config.add_subscriber(".subscribers.create_salessegment_group", ".subscribers.PerformanceCreate")    
    config.add_view(".views.performance_detail", match_param="action=detail", permission="performance_update", 
                    route_name="performance_update", 
                    decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
                    renderer="altaircms:templates/performance/view.html")
    config.add_crud("salessegment", title="salessegment", model="..models.SalesSegment", 
                    has_auto_generated_permission=False,  #todo:remove-it
                    circle_type="circle-event", 
                    bind_actions=["create", "delete", "update"], 
                    events=dict(create_event=config.maybe_dotted(".subscribers.SalesSegmentCreate"), 
                                update_event=config.maybe_dotted(".subscribers.SalesSegmentUpdate")), 
                    form=".forms.SalesSegmentForm", mapper=".mappers.sale_mapper")
    config.add_crud("ticket", title="ticket", model="..models.Ticket", 
                    has_auto_generated_permission=False,  #todo:remove-it
                    circle_type="circle-event", 
                    bind_actions=["create", "delete", "update"], 
                    events=dict(create_event=config.maybe_dotted(".subscribers.TicketCreate"), 
                                update_event=config.maybe_dotted(".subscribers.TicketUpdate")), 
                    form=".forms.TicketForm", mapper=".mappers.ticket_mapper")
    ## topic
    config.add_crud("topic_unit", title="topic", model="..topic.models.Topic",
                    has_auto_generated_permission=False,  #todo:remove-it
                    circle_type="circle-item", 
                    bind_actions=["create", "delete", "update"], 
                    form=".forms.TopicForm", mapper=".mappers.topic_mapper", 
                    events=dict(create_event=config.maybe_dotted(".subscribers.TopicCreate"), 
                                update_event=config.maybe_dotted(".subscribers.TopicUpdate"), 
                                ))

    config.add_crud("topcontent_unit", title="topcontent", model="..topic.models.Topcontent",
                    has_auto_generated_permission=False,  #todo:remove-it
                    circle_type="circle-item", 
                    bind_actions=["create", "delete", "update"], 
                    form=".forms.TopcontentForm", mapper=".mappers.topcontent_mapper", 
                    events=dict(create_event=config.maybe_dotted(".subscribers.TopicCreate"), 
                                update_event=config.maybe_dotted(".subscribers.TopicUpdate"), 
                                ))
    config.add_crud("promotion_unit",  title="promotion",  model="..topic.models.Promotion",
                    has_auto_generated_permission=False,  #todo:remove-it
                    circle_type="circle-item", 
                    bind_actions=["create", "delete", "update"], 
                    form=".forms.PromotionForm", mapper=".mappers.promotion_mapper", 
                    events=dict(create_event=config.maybe_dotted(".subscribers.TopicCreate"), 
                                update_event=config.maybe_dotted(".subscribers.TopicUpdate"), 
                                ))
    config.add_subscriber(".subscribers.update_kind", ".subscribers.TopicCreate")
    config.add_subscriber(".subscribers.update_kind", ".subscribers.TopicUpdate")

    config.add_crud("category", title="category", model="..models.Category",
                    circle_type="circle-master", 
                    bind_actions=["delete", "update", "create"], 
                    form=".forms.CategoryForm", mapper=".mappers.category_mapper")
    config.add_route("category_list", "/category")
    config.add_view(".views.category_list_view", route_name="category_list", permission="category_read", 
                    decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
                    renderer="altaircms:templates/category/list.html")
    config.add_crud("category.link", title="external link", model="..models.Category",
                    circle_type="circle-master", 
                    has_auto_generated_permission=False, 
                    bind_actions=["create", "update"], 
                    endpoint="category_list", 
                    form=".forms.ExternalLinkForm", mapper=".mappers.category_mapper")
    config.add_crud("category.banner", title="external banner", model="..models.Category",
                    circle_type="circle-master", 
                    has_auto_generated_permission=False, 
                    bind_actions=["create", "update"], 
                    endpoint="category_list", 
                    form=".forms.ExternalBannerForm", mapper=".mappers.category_mapper")
    config.add_crud("hotword", title="hotword", model="..tag.models.HotWord",
                    circle_type="circle-item", 
                    form=".forms.HotWordForm", mapper=".mappers.hotword_mapper")
    config.add_crud("pagedefaultinfo", title="pagedefaultinfo", model="..page.models.PageDefaultInfo",
                    circle_type="circle-master", 
                    has_auto_generated_permission=False, 
                    form=".forms.PageDefaultInfoForm", mapper=".mappers.pagedefaultinfo_mapper")
    config.add_crud("pagetype", title="pagetype", model="..page.models.PageType",
                    circle_type="circle-master", 
                    has_auto_generated_permission=False, 
                    form=".forms.PageTypeForm", mapper=".mappers.pagetype_mapper")
    config.add_crud("pageset", title="pageset", model="..page.models.PageSet",
                    circle_type="circle-page", 
                    bind_actions=["update"], 
                    has_auto_generated_permission=False, 
                    events=dict(update_event=config.maybe_dotted(".subscribers.PageSetUpdate")), 
                    override_templates=dict(update="altaircms:templates/pagesets/update_input_with_genre.html"), 
                    form=".forms.PageSetForm", mapper=".mappers.pageset_mapper")
    config.add_crud("static_page", title="static_page", model="..page.models.StaticPage", 
                    circle_type="circle-page", 
                    bind_actions=["update"], 
                    has_auto_generated_permission=False, 
                    form="..page.staticupload.forms.StaticPageForm", mapper=".mappers.staticpage_mapper", 
                    )

    config.add_crud("static_pageset", title="static_pageset", model="..page.models.StaticPageSet", 
                    circle_type="circle-page", 
                    bind_actions=["update", "delete"], 
                    has_auto_generated_permission=False, 
                    form="..page.staticupload.forms.StaticPageSetForm", mapper=".mappers.staticpageset_mapper", 
                    events=dict(update_event=config.maybe_dotted(".subscribers.StaticPageSetUpdate"), 
                                delete_event=config.maybe_dotted(".subscribers.StaticPageSetDelete")), 
                    )

    ## subscriber
    config.add_subscriber(".subscribers.after_delete_static_pageset", ".subscribers.StaticPageSetDelete")
    config.add_subscriber(".subscribers.update_pageset_genretag", ".subscribers.PageSetUpdate")
    config.add_subscriber(".subscribers.event_term_bubbling_update", ".subscribers.PerformanceCreate")
    config.add_subscriber(".subscribers.event_term_bubbling_update", ".subscribers.PerformanceUpdate")
    config.add_subscriber(".subscribers.sales_term_bubbling_update", ".subscribers.SalesSegmentCreate")
    config.add_subscriber(".subscribers.sales_term_bubbling_update", ".subscribers.SalesSegmentUpdate")
    config.add_subscriber(".subscribers.after_change_ticket", ".subscribers.TicketCreate")
    config.add_subscriber(".subscribers.after_change_ticket", ".subscribers.TicketUpdate")

"""
memo:
performance, ticket, sale, pagedefaultinfoはorganization_idを持っていない。
これは、cmsサイト上に一覧画面を表示しないことを表している。
(一覧が必要なら、organization_idを追加する)
"""
