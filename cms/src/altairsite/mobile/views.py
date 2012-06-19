# -*- coding:utf-8 -*-
from pyramid.view import view_config
from altaircms.models import Category
from altaircms.page.models import PageSet
from altaircms.topic.models import Topic, Topcontent
from datetime import datetime
from . import helpers as h
from . import api
from altairsite.search import api as search_api

@view_config(route_name="mobile_index", renderer="altaircms:templates/mobile/index.mako")
def mobile_index(request):
    today = datetime.now()
    pageset = PageSet.query.filter(Category.name=="index").filter(PageSet.id==Category.pageset_id).first()

    topics = Topic.matched_qs(d=today, kind=u"トピックス", page=pageset)
    picks = Topcontent.matched_qs(d=today, kind=u"注目のイベント", page=pageset)
    return {"page": pageset.current(), "topics": topics, "picks":picks}


@view_config(route_name="mobile_detail", renderer="altaircms:templates/mobile/detail.mako")
def mobile_detail(request):
    today = datetime.now()
    pageset = PageSet.query.filter_by(id=request.matchdict["pageset_id"]).first()
    return {"page": pageset.current(), "event": pageset.event, "performances": pageset.event.performances, 
            "today": today}


def enable_categories(info, request):
    return request.matchdict["category"] in ("music", "sports", "stage", "event")

@view_config(route_name="mobile_category", custom_predicates=(enable_categories,), 
             renderer="altaircms:templates/mobile/category.mako")
def mobile_category(request):
    today = datetime.now()
    category_name = request.matchdict["category"]
    root = Category.query.filter_by(name=category_name).first()
    picks = Topcontent.matched_qs(d=today, kind=u"注目のイベント", page=root.pageset)

    topics = Topic.matched_qs(d=today, kind=u"トピックス", page=root.pageset).filter_by(is_global=False)
    events_on_sale = api.events_on_sale_this_week(request, category_name, today)
    return {"synonym": h.CATEGORY_SYNONYM.get(category_name), 
            "picks": picks, 
            "events_on_sale": events_on_sale, 
            "root": root, 
            "topics": topics, 
            "subcategories": Category.query.filter_by(parent=root)}


@view_config(request_param="q", route_name="mobile_search", 
             renderer="altaircms:templates/mobile/search.mako")
def search_by_freeword(context, request):
    """ フリーワード検索 + categoryごとの数
    """
    freeword = request.params["q"]
    root_category = request.params.get("r")
    root = Category.query.filter_by(name=root_category).first() if root_category else None

    children = h.get_children_category_from_root(root)

    qs = search_api.search_by_freeword(request, freeword)
    qs = h.pageset_query_filter_by_root(qs, root)

    classifieds = [(c, qs.filter(PageSet.category==c)) for c in children]

    top = u'<a href="%s">トップ</a>' % request.route_path("mobile_index")
    breadcrumbs = api.build_breadcrumbs(request, top, root)

    return {"pagesets": qs, "classifieds": classifieds, "synonym": h.CATEGORY_SYNONYM, 
            "breadcrumbs": breadcrumbs, "freeword":freeword}

from pyramid.renderers import render_to_response
import os.path

@view_config(route_name="mobile_semi_static")
def mobile_semi_static(request):
    ## normalize
    filename = request.matchdict["filename"]
    template_path = os.path.join("altaircms:templates/mobile/static/", filename)
    if not template_path.endswith(".mako"):
        template_path = os.path.splitext(template_path)[0]+".mako"

    return render_to_response(template_path, {}, request)
