# -*- coding:utf-8 -*-
#
from pyramid.view import view_config

from altaircms.widget.api import get_has_widget_pages_finder
from altaircms.tag.api import get_tagmanager
import altaircms.helpers as h
from altaircms.auth.api import get_or_404
from altaircms.page.models import Page

from .viewhelpers import PromotionGrid
from .viewhelpers import PromotionHTMLRenderer
from .searcher import PromotionPageListSearcher
from .searcher import PromotionPageDetailSearcher

## todo: 現在表示中のpromotion, 全部表示の２種類

@view_config(route_name="promotion_list", renderer="altaircms:templates/topic/promotion/pages.html", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
             permission="promotion_read")
def promotion_list(context, request):
    finder = get_has_widget_pages_finder(request, name="promotion")
    searcher = PromotionPageListSearcher(request, finder)

    qs = searcher.get_objects_for_grid(request.allowable(Page, qs=finder(request)))
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

    tag_manager = get_tagmanager("promotion", request=request) #todo: sort
    promotions = tag_manager.search_by_tag_label(widget.kind.label)
    return dict(promotions=promotions, page=page,
                promotion_renderer=PromotionHTMLRenderer(request), 
                current_widget=widget, widgets=widgets)
