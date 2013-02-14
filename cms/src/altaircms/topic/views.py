# -*- coding:utf-8 -*-
#
import sqlalchemy.orm as orm
from pyramid.view import view_config
from datetime import datetime
import altaircms.helpers as h
from altaircms.auth.api import get_or_404
from altaircms.page.models import Page
from .api import get_topic_searcher

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
    search_word = request.GET.get("search", "")
    qs = searcher.get_objects_for_grid(request.allowable(Page, qs=searcher.finder(request)))
    if ":all:" in request.GET:
        qs = searcher.no_filter_without_tag(qs, request.GET)
    else:
        qs = searcher.filter_default(qs, request.GET)

    pages = h.paginate(request, qs, item_count=qs.count())
    grid = context.Grid.create(pages.paginated())

    recently_tags = context.tag_manager.recent_change_tags().filter_by(publicp=True).limit(10)
    return dict(grid=grid, pages=pages, recently_tags=recently_tags, search_word=search_word)


@view_config(route_name="topic_tag_list", renderer="altaircms:templates/tag/tags.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
             permission="topic_read")
@view_config(route_name="topcontent_tag_list", renderer="altaircms:templates/tag/tags.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
             permission="topcontent_read")
@view_config(route_name="promotion_tag_list", renderer="altaircms:templates/tag/tags.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
             permission="promotion_read")
def tag_list_view(context, request):
    tags = context.tag_manager.recent_change_tags().filter_by(publicp=True)
    return dict(tags=tags)

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

    searcher = get_topic_searcher(request, context.widgettype)

    if ":all:" in request.GET:
        topics = searcher._start_query()
        topics = searcher.filter_by_tag(topics, widget.tag)
        # if widget.system_tag_id:
        #     topics = searcher.filter_by_system_tag(topics, widget.system_tag)
        topics = context.TargetTopic.order_by_logic(topics)
    else:
        d = datetime.now()
        topics = searcher.query_publishing_topics(d, widget.tag, widget.system_tag)
        topics = topics.options(orm.joinedload(context.TargetTopic.tags))
    return dict(topics=topics, page=page,
                topic_renderer=context.TopicHTMLRenderer(request), 
                current_widget=widget, widgets=widgets)
