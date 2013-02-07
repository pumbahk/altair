# -*- coding:utf-8 -*-
#
from pyramid.view import view_config

import altaircms.helpers as h
from altaircms.auth.api import get_or_404
from altaircms.page.models import Page

@view_config(route_name="topic_list", renderer="altaircms:templates/topic/topic/pages.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
             permission="topic_read")
@view_config(route_name="topcontent_list", renderer="altaircms:templates/topic/topcontent/pages.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
             permission="topcontent_read")
@view_config(route_name="promotion_list", renderer="altaircms:templates/topic/promotion/pages.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
             permission="promotion_read")
def list_view(context, request):
    searcher = context.list_searcher
    qs = searcher.get_objects_for_grid(request.allowable(Page, qs=searcher.finder(request)))
    if ":all:" in request.GET:
        qs = searcher.no_filter_without_tag(qs, request.GET)
    else:
        qs = searcher.filter_default(qs, request.GET)
    pages = h.paginate(request, qs, item_count=qs.count())
    grid = context.Grid.create(pages.paginated())
    return dict(grid=grid, pages=pages)

@view_config(route_name="topic_detail", renderer="altaircms:templates/topic/topic/page_detail.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
             permission="topic_read")
@view_config(route_name="topcontent_detail", renderer="altaircms:templates/topic/topcontent/page_detail.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
             permission="topcontent_read")
@view_config(route_name="promotion_detail", renderer="altaircms:templates/topic/promotion/page_detail.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
             permission="promotion_read")
def detail_view(context, request):
    page_id = request.matchdict["page_id"]
    widget_id = request.GET.get("widget_id")

    searcher = context.detail_searcher

    page = get_or_404(request.allowable(Page), Page.id==page_id)
    widgets = searcher.get_widgets(page_id)
    widget = searcher.get_current_widget(widgets, widget_id=widget_id)

    topics = context.tag_manager.search_by_tag_label(widget.tag.label)

    if ":all:" in request.GET:
        topics = context.TargetTopic.order_by_logic(topics)
    else:
        topics = context.TargetTopic.publishing(qs=topics)
    return dict(topics=topics, page=page,
                topic_renderer=context.TopicHTMLRenderer(request), 
                current_widget=widget, widgets=widgets)
