# -*- coding:utf-8 -*-
from pyramid.view import view_config
<<<<<<< HEAD
<<<<<<< HEAD
from altaircms.models import Category
from altaircms.page.models import PageSet
from altaircms.topic.models import Topic, Topcontent
from datetime import datetime
from . import helpers as h
<<<<<<< HEAD
from altaircms import helpers as gh
from altairsite.search import api as search_api


@view_config(route_name="mobile_index", renderer="altaircms:templates/mobile/index.mako")
def mobile_index(request):
    import warnings
    warnings.warn("this is adhoc code. so need fix.")
    today = datetime.now()
    pageset = PageSet.query.filter_by(id=1).first()

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
    category = request.matchdict["category"]
    root = Category.query.filter_by(name=category).first()
    picks = Topcontent.matched_qs(d=today, kind=u"注目のイベント", page=root.pageset)

    topics = Topic.matched_qs(d=today, kind=u"トピックス", page=root.pageset).filter_by(is_global=False)
    events_on_sale = h.events_on_sale_this_week(request, category, today)
    return {"synonym": h.CATEGORY_SYNONYM.get(category), 
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
    root_category = request.params.get("r")
    root = Category.query.filter_by(name=root_category).first() if root_category else None
    if root is None:
        ## this is adhoc code. ugly.
        children = Category.query.filter_by(parent=None, hierarchy=u"大").filter(Category.name!="index")
    else:
        children = Category.query.filter_by(parent=root)

    freeword = request.params["q"]
    qs = search_api.search_by_freeword(request, freeword)

    classifieds = [(c, qs.filter(PageSet.category==c)) for c in children]

    breadcrumbs = [u'<a href="%s">トップ</a>' % request.route_path("mobile_index")]
    if root:
        breadcrumbs = breadcrumbs + list(h.category_to_breadcrumbs(request, root, freeword))
    breadcrumbs = gh.base.RawText(u"&gt;".join(breadcrumbs))

    return {"pagesets": qs, "classifieds": classifieds, "synonym": h.CATEGORY_SYNONYM, 
            "breadcrumbs": breadcrumbs, "freeword":freeword}
=======
=======
from altaircms.models import Category
>>>>>>> カテゴリトップ上部メニュー変更
from altaircms.page.models import PageSet
from altaircms.topic.models import Topic, Topcontent
from datetime import datetime
from .helpers import CATEGORY_SYNONYM
=======
>>>>>>> mobileカテゴリトップ、これから販売されるページ,topics。

@view_config(route_name="mobile_index", renderer="altaircms:templates/mobile/index.mako")
def mobile_index(request):
    import warnings
    warnings.warn("this is adhoc code. so need fix.")
    today = datetime.now()
    pageset = PageSet.query.filter_by(id=1).first()

    topics = Topic.matched_qs(d=today, kind=u"トピックス", page=pageset)
    picks = Topcontent.matched_qs(d=today, kind=u"注目のイベント", page=pageset)
    return {"page": pageset.current(), "topics": topics, "picks":picks}


@view_config(route_name="mobile_detail", renderer="altaircms:templates/mobile/detail.mako")
def mobile_detail(request):
    today = datetime.now()
    pageset = PageSet.query.filter_by(id=request.matchdict["pageset_id"]).first()
    return {"page": pageset.current(), "event": pageset.event, "performances": pageset.event.performances, 
            "today": today}

<<<<<<< HEAD
>>>>>>> mobile詳細画面途中
=======

def enable_categories(info, request):
    return request.matchdict["category"] in ("music", "sports", "stage", "event")
@view_config(route_name="mobile_category", custom_predicates=(enable_categories,), 
             renderer="altaircms:templates/mobile/category.mako")
def mobile_category(request):
<<<<<<< HEAD
<<<<<<< HEAD
    return {}
<<<<<<< HEAD
>>>>>>> カテゴリトップ作成中
=======
=======
=======
    today = datetime.now()
>>>>>>> topcontentの表示登録
    category = request.matchdict["category"]
    root = Category.query.filter_by(name=category).first()
    picks = Topcontent.matched_qs(d=today, kind=u"注目のイベント", page=root.pageset)

    topics = Topic.matched_qs(d=today, kind=u"トピックス", page=root.pageset).filter_by(is_global=False)
    events_on_sale = h.events_on_sale_this_week(request, category, today)
    return {"synonym": h.CATEGORY_SYNONYM.get(category), 
            "picks": picks, 
            "events_on_sale": events_on_sale, 
            "topics": topics, 
            "subcategories": Category.query.filter_by(parent=root)}
<<<<<<< HEAD
>>>>>>> カテゴリトップ上部メニュー変更


>>>>>>> garden
=======
>>>>>>> mobileカテゴリトップ、これから販売されるページ,topics。
