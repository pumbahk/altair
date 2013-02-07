# -*- coding:utf-8 -*-
#
from pyramid.view import view_config

from altaircms.widget.api import get_has_widget_pages_finder
from altaircms.tag.api import get_tagmanager
import altaircms.helpers as h
from altaircms.auth.api import get_or_404
from altaircms.topic.models import Topcontent
from altaircms.topic.models import Promotion
from altaircms.page.models import Page

from .viewhelpers import TopcontentGrid
from .viewhelpers import TopcontentHTMLRenderer
from .searcher import TopcontentPageDetailSearcher

from .viewhelpers import PromotionGrid
from .viewhelpers import PromotionHTMLRenderer
from .searcher import PromotionPageDetailSearcher

@view_config(route_name="topcontent_list", renderer="altaircms:templates/topic/topcontent/pages.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
             permission="topcontent_read")
def topcontent_list(context, request):
    searcher = context.searcher
    qs = searcher.get_objects_for_grid(request.allowable(Page, qs=searcher.finder(request)))
    if ":all:" in request.GET:
        qs = searcher.no_filter_without_tag(qs, request.GET)
    else:
        qs = searcher.filter_default(qs, request.GET)
    pages = h.paginate(request, qs, item_count=qs.count())
    grid = TopcontentGrid.create(pages.paginated())
    return dict(grid=grid, pages=pages)

@view_config(route_name="topcontent_detail", renderer="altaircms:templates/topic/topcontent/page_detail.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
             permission="topcontent_read")
def topcontent_detail(context, request):
    widget_id = request.GET.get("widget_id")
    page_id = request.matchdict["page_id"]

    finder = get_has_widget_pages_finder(request, name="topcontent")
    searcher = TopcontentPageDetailSearcher(request, finder)

    page = get_or_404(request.allowable(Page), Page.id==page_id)
    widgets = searcher.get_widgets(page_id)
    widget = searcher.get_current_widget(widgets, widget_id=widget_id)

    tag_manager = get_tagmanager("topcontent", request=request)
    topcontents = tag_manager.search_by_tag_label(widget.tag.label)

    if ":all:" in request.GET:
        topcontents = Topcontent.order_by_logic(topcontents)
    else:
        topcontents = Topcontent.publishing(qs=topcontents)
    return dict(topcontents=topcontents, page=page,
                topcontent_renderer=TopcontentHTMLRenderer(request), 
                current_widget=widget, widgets=widgets)

@view_config(route_name="promotion_list", renderer="altaircms:templates/topic/promotion/pages.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
             permission="promotion_read")
def promotion_list(context, request):
    searcher = context.searcher
    qs = searcher.get_objects_for_grid(request.allowable(Page, qs=searcher.finder(request)))
    if ":all:" in request.GET:
        qs = searcher.no_filter_without_tag(qs, request.GET)
    else:
        qs = searcher.filter_default(qs, request.GET)
    pages = h.paginate(request, qs, item_count=qs.count())
    grid = PromotionGrid.create(pages.paginated())
    return dict(grid=grid, pages=pages)

@view_config(route_name="promotion_detail", renderer="altaircms:templates/topic/promotion/page_detail.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
             permission="promotion_read")
def promotion_detail(context, request):
    widget_id = request.GET.get("widget_id")
    page_id = request.matchdict["page_id"]

    finder = get_has_widget_pages_finder(request, name="promotion")
    searcher = PromotionPageDetailSearcher(request, finder)

    page = get_or_404(request.allowable(Page), Page.id==page_id)
    widgets = searcher.get_widgets(page_id)
    widget = searcher.get_current_widget(widgets, widget_id=widget_id)

    tag_manager = get_tagmanager("promotion", request=request)
    promotions = tag_manager.search_by_tag_label(widget.tag.label)

    if ":all:" in request.GET:
        promotions = Promotion.order_by_logic(promotions)
    else:
        promotions = Promotion.publishing(qs=promotions)
    return dict(promotions=promotions, page=page,
                promotion_renderer=PromotionHTMLRenderer(request), 
                current_widget=widget, widgets=widgets)
