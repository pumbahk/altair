# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
from ..plugins.api import get_widget_aggregator_dispatcher
from altaircms.helpers.viewhelpers import RegisterViewPredicate
from altaircms.helpers.viewhelpers import FlashMessage
from . import forms
from . import searcher
import altaircms.widget.forms as wf
from ..models import DBSession

from altaircms.page.models import PageType
from altaircms.page.models import PageSet
from altaircms.page.models import Page
from altaircms.page.models import StaticPage
from altaircms.layout.models import Layout
from altaircms.widget.models import WidgetDisposition
from altaircms.event.models import Event
from altaircms.auth.api import get_or_404

from altaircms.helpers.viewhelpers import get_endpoint, set_endpoint

from altaircms.lib.fanstatic_decorator import with_bootstrap
from altaircms.lib.fanstatic_decorator import with_jquery
from altaircms.lib.fanstatic_decorator import with_fanstatic_jqueries
# from altaircms.lib.fanstatic_decorator import with_wysiwyg_editor
import altaircms.helpers as h
from .staticupload.api import get_static_page_utility
from . import helpers as myhelpers
from altaircms.widget.forms import WidgetDispositionSaveDefaultForm
from altaircms.widget.forms import WidgetDispositionSaveForm

class AfterInput(Exception):
    pass

##
## todo: CRUDのview整理する
##
@view_defaults(decorator=with_bootstrap.merge(with_jquery))
class PageAddView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name="page_add", request_method="GET", request_param="pagetype=event_detail", match_param="action=input", permission="page_create")
    def input_form_with_event(self):
        set_endpoint(self.request)
        event_id = self.request.matchdict["event_id"]
        event = self.request._event = get_or_404(self.request.allowable(Event), (Event.id==event_id))
        self.request._form = forms.PageForm(event=event)
        self.request._setup_form = forms.PageInfoSetupWithEventForm(name=event.title, event=event)
        raise AfterInput

    @view_config(route_name="page_add_orphan", request_param="pagetype=event_detail", request_method="GET", match_param="action=input", permission="page_create")
    def input_form_orphan_with_event(self):
        set_endpoint(self.request)
        self.request._form = forms.PageForm()
        self.request._setup_form = forms.PageInfoSetupWithEventForm()
        raise AfterInput

    @view_config(route_name="page_add_orphan", request_param="pagetype", request_method="GET", match_param="action=input", permission="page_create")
    def input_form(self):
        set_endpoint(self.request)
        self.request._form = forms.PageForm()
        self.request._setup_form = forms.PageInfoSetupForm()
        raise AfterInput
        
    @view_config(route_name="page_add", context=AfterInput, decorator=with_bootstrap.merge(with_jquery), 
                 renderer="altaircms:templates/page/add_orphan.html")
    def after_input_with_event(self):
        request = self.request
        return {"event": request._event, 
                "form": request._form, 
                "setup_form": request._setup_form}

    @view_config(route_name="page_add_orphan", context=AfterInput, decorator=with_bootstrap.merge(with_jquery), 
                 renderer="altaircms:templates/page/add_orphan.html")
    def after_input(self):
        request = self.request
        return {"form": request._form, 
                "setup_form": request._setup_form}

    @view_config(route_name="page_add", permission="page_create", match_param="action=confirm", request_method="POST", 
                 renderer="altaircms:templates/page/confirm.html")
    def confirm_with_event(self):
        self.request.POST
        form = forms.PageForm(self.request.POST)
        if form.validate():
            return {"form": form}
        else:
            event_id = self.request.matchdict["event_id"]
            self.request._form = form
            self.request._event = get_or_404(self.request.allowable(Event), Event.id==event_id)
            self.request._setup_form = forms.PageInfoSetupForm(name=form.data["name"])
            raise AfterInput

    @view_config(route_name="page_add_orphan", permission="page_create", match_param="action=confirm", request_method="POST", 
                 renderer="altaircms:templates/page/confirm.html")
    def confirm(self):
        self.request.POST
        form = forms.PageForm(self.request.POST)
        if form.validate():
            if self.request.GET.get("pagetype"):
                pagetype = self.request.allowable(PageType, PageType.name==self.request.GET.get("pagetype")).first()
                if pagetype.is_portal and form.data["genre"]:
                    FlashMessage.info(u"%sのカテゴリトップページとして登録されます。(既にカテゴリトップページが存在している場合にはこれから作られるページが優先されます)" % form.data["genre"].label, request=self.request)
            return {"form": form}
        else:
            self.request._form = form
            self.request._setup_form = forms.PageInfoSetupForm(name=form.data["name"])
            raise AfterInput

    @view_config(route_name="page_add", permission="page_create", request_method="POST", match_param="action=create")
    def create_page_with_event(self):
        logging.debug('create_page')
        form = forms.PageForm(self.request.POST)
        event_id = self.request.matchdict["event_id"]
        if form.validate():
            page = self.context.create_page(form)
            ## flash messsage
            mes = u'page created <a href="%s">作成されたページを編集する</a>' % self.request.route_path("pageset_detail", pageset_id=page.pageset.id, kind="event")
            FlashMessage.success(mes, request=self.request)
            return HTTPFound(get_endpoint(self.request) or self.request.route_path("event", id=self.request.matchdict["event_id"]))
        else:
            event_id = self.request.matchdict["event_id"]
            self.request._form = form
            self.request._event = get_or_404(self.request.allowable(Event), Event.id==event_id)
            self.request._setup_form = forms.PageInfoSetupForm(name=form.data["name"])
            raise AfterInput

    @view_config(route_name="page_add_orphan", permission="page_create", request_method="POST", match_param="action=create")
    def create_page(self):
        try:
            logging.debug('create_page')
            form = forms.PageForm(self.request.POST)
            if form.validate():
                page = self.context.create_page(form)
                ## flash messsage
                mes = u'page created <a href="%s">作成されたページを編集する</a>' % self.request.route_path("pageset_detail", pageset_id=page.pageset.id, kind="other")
                FlashMessage.success(mes, request=self.request)
                return HTTPFound(get_endpoint(self.request) or self.request.route_path("pageset_list", pagetype=page.pagetype.name))
            else:
                self.request._form = form
                self.request._setup_form = forms.PageInfoSetupForm(name=form.data["name"])
                raise AfterInput
        except Exception, e:
            logger.exception(str(e))
            raise


 

@view_defaults(permission="page_create", decorator=with_bootstrap)
class PageDuplicateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    # @view_config(route_name="page", renderer='altaircms:templates/page/list.html', request_method="POST")
    # def create(self):
    #     form = forms.PageForm(self.request.POST)
    #     if form.validate():
    #         page = self.context.create_page(form)
    #         ## flash messsage
    #         mes = u'page created <a href="%s">作成されたページを編集する</a>' % self.request.route_path("page_edit_", page_id=page.id)
    #         FlashMessage.success(mes, request=self.request)
    #         return HTTPFound(self.request.route_path("page"))
    #     else:
    #         setup_form = forms.PageInfoSetupForm(name=form.data["name"], parent=form.data["parent"])
    #         return dict(
    #             pages=self.context.Page.query,
    #             form=form, 
    #             setup_form = setup_form
    #             )

    @view_config(route_name="page_duplicate", request_method="GET", renderer="altaircms:templates/page/duplicate_confirm.html")
    def duplicate_confirm(self):
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.matchdict["id"])
        return {"page": page}
        
    @view_config(route_name="page_duplicate", request_method="POST")
    def duplicate(self):
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.matchdict["id"])
        self.context.clone_page(page)
        FlashMessage.success(u"ページをコピーしました", request=self.request)
        return HTTPFound(self.request.GET.get("endpoint") or "/")

@view_defaults(route_name="page_delete", permission="page_delete", decorator=with_bootstrap)
class PageDeleteView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="altaircms:templates/page/delete_confirm.html", request_method="GET")
    def delete_confirm(self):
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.matchdict["id"])
        return {"page": page}

    @view_config(request_method="POST")
    def delete(self):
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.matchdict["id"])
        self.context.delete_page(page)

        ## flash messsage
        FlashMessage.success("page deleted", request=self.request)

        return HTTPFound(location=h.page.to_list_page(self.request, page))

@view_defaults(route_name="pageset_delete", permission="page_delete", decorator=with_bootstrap)
class PageSetDeleteView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="altaircms:templates/pagesets/delete_confirm.html", request_method="GET")
    def delete_confirm(self):
        pageset = get_or_404(self.request.allowable(PageSet), PageSet.id==self.request.matchdict["pageset_id"])
        return {"pageset": pageset, "myhelpers": myhelpers}

    @view_config(request_method="POST")
    def delete(self):
        pageset = get_or_404(self.request.allowable(PageSet), PageSet.id==self.request.matchdict["pageset_id"])
        try:
            self.context.delete_pageset(pageset)
            ## Integritty errorをキャッチしたいので
            import transaction
            transaction.commit()
        except Exception, e:
            FlashMessage.error(str(e), request=self.request)
            raise HTTPFound(self.request.route_url("pageset_delete", pageset_id=self.request.matchdict["pageset_id"]))
        ## flash messsage
        FlashMessage.success(u"%sのページセットがまるごと削除されました" % pageset.name, request=self.request)
        return HTTPFound(self.request.route_url("dashboard"))



@view_config(route_name="page_update", context=AfterInput, renderer="altaircms:templates/page/input.html", 
             decorator=with_bootstrap)
def _input(request):
    page, form = request._store
    return dict(
        page=page, form=form,
        )

@view_defaults(route_name="page_update", permission="page_update", decorator=with_bootstrap)
class PageUpdateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _input_page(self, page, form):
        self.request._store = page, form
        raise AfterInput
        
    @view_config(request_method="GET")
    def input(self):
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.matchdict["id"])
        params = page.to_dict()
        form = forms.PageUpdateForm(**params)
        return self._input_page(page, form)

    @view_config(request_method="POST", renderer="altaircms:templates/page/update_confirm.html",       
                    custom_predicates=[RegisterViewPredicate.confirm])
    def update_confirm(self):
        form = forms.PageUpdateForm(self.request.POST)
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.matchdict["id"])
        if form.validate():
            return dict( page=page, params=self.request.POST.items())
        else:
            return self._input_page(page, form)

    @view_config(request_method="POST", custom_predicates=[RegisterViewPredicate.execute])
    def update(self):
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.matchdict["id"])
        form = forms.PageUpdateForm(self.request.POST)
        if form.validate():
            page = self.context.update_page(page, form)
            ## flash messsage
            FlashMessage.success("page updated", request=self.request)
            return HTTPFound(location=h.page.to_edit_page(self.request, page))
        else:
            return self._input_page(page, form)

@view_defaults(permission="page_update", route_name="page_partial_update", request_method="POST")
class PagePartialUpdateAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(match_param="part=layout", renderer="json")
    def layout_update(self):
        layout_id = self.request.POST["layout_id"]
        layout = self.request.allowable(Layout).filter_by(id=layout_id).first()
        if layout is None:
            return {"status": False, "message": "layout is not found", "data": {"layout_id": layout_id}}
        page = self.request.allowable(Page).filter_by(id=self.request.matchdict["id"]).first()
        if page is None:
            return {"status": False, "message": "page is not found", "data": {"layout_id": layout_id}}
        page.layout = layout
        DBSession.add(page)
        return {"status": True, "data": {"layout_id": layout_id}}


@view_defaults(permission="page_read", route_name="pageset_list", decorator=with_bootstrap, request_method="GET")
class ListView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    @view_config(match_param="pagetype=static", renderer="altaircms:templates/pagesets/static_pageset_list.html")
    def static_page_list(self):
        pagetype = get_or_404(self.request.allowable(PageType), (PageType.name==self.request.matchdict["pagetype"]))
        static_directory = get_static_page_utility(self.request)
        return {"static_directory": static_directory, 
                "pages": static_directory.get_managemented_files(self.request).order_by(sa.desc(StaticPage.updated_at)), 
                "pagetype": pagetype}

    @view_config(match_param="pagetype=event_detail", renderer="altaircms:templates/pagesets/event_pageset_list.html")
    def event_bound_page_list(self):
        """ event詳細ページと結びついているpage """
        pagetype = get_or_404(self.request.allowable(PageType), (PageType.name==self.request.matchdict["pagetype"]))
        qs = self.request.allowable(PageSet).filter(PageSet.pagetype_id==pagetype.id, 
                                                    PageSet.event_id!=None)
        params = dict(self.request.GET)
        if "page" in params:
            params.pop("page") ## pagination
        if params:
            search_form = forms.PageSetSearchForm(self.request.GET)
            if search_form.validate():
                qs = searcher.make_pageset_search_query(self.request, search_form.data, qs=qs)
        else:
            search_form = forms.PageSetSearchForm()

        qs = qs.order_by(sa.desc(PageSet.updated_at))
        pages = h.paginate(self.request, qs, item_count=qs.count(), items_per_page=50)
        return {"pages": pages, "pagetype": pagetype, "search_form": search_form}

    @view_config(renderer="altaircms:templates/pagesets/other_pageset_list.html")
    def other_page_list(self):
        """event詳細ページとは結びついていないページ(e.g. トップ、カテゴリトップ) """
        pagetype = get_or_404(self.request.allowable(PageType), (PageType.name==self.request.matchdict["pagetype"]))
        qs = self.request.allowable(PageSet).filter(PageSet.pagetype_id==pagetype.id)
        params = dict(self.request.GET)
        if "page" in params:
            params.pop("page") ## pagination
        if params:
            search_form = forms.PageSetSearchForm(self.request.GET)
            if search_form.validate():
                qs = searcher.make_pageset_search_query(self.request, search_form.data, qs=qs)
        else:
            search_form = forms.PageSetSearchForm()

        qs = qs.order_by(sa.desc(PageSet.updated_at))
        pages = h.paginate(self.request, qs, item_count=qs.count(), items_per_page=50)
        return {"pages": pages, "pagetype": pagetype, "search_form": search_form}


def with_pageset_predicate(kind): #don't support static page
    def decorate(info, request):
        if not hasattr(request, "_pageset"):
            pageset_id = request.matchdict["pageset_id"]
            request._pageset = request.allowable(PageSet).filter_by(id=pageset_id).first()
        pageset = request._pageset
        if pageset is None:
            return False
        if pageset.event_id == None:
            return kind == "other"
        else:
            return kind == "event"
    return decorate

@view_defaults(permission="page_read", route_name="pageset_detail", decorator=with_bootstrap, request_method="GET")
class PageSetDetailView(object):
    def __init__(self, request):
        self.request = request

    def static_page_detail(self):
        pass

    @view_config(renderer="altaircms:templates/pagesets/event_page_detail.html", 
                 custom_predicates=(with_pageset_predicate("event"),))
    def event_bound_page_detail(self):
        """ event詳細ページと結びついているpage """
        pageset = self.request._pageset ## predicate
        return {"pageset":pageset, 
                "myhelpers": myhelpers}


    @view_config(renderer="altaircms:templates/pagesets/other_page_detail.html", 
                 custom_predicates=(with_pageset_predicate("other"),))
    def other_page_detail(self):
        """event詳細ページとは結びついていないページ(e.g. トップ、カテゴリトップ) """
        pageset = self.request._pageset ## predicate
        return {"pageset":pageset, 
                "myhelpers": myhelpers}



@view_config(route_name="page_detail", renderer='altaircms:templates/page/view.html', permission='authenticated', 
             decorator=with_fanstatic_jqueries.merge(with_bootstrap))
def page_detail(request):
    """ page詳細ページ
    """
    page = get_or_404(request.allowable(Page), Page.id==request.matchdict["page_id"])
    return {"page": page, "myhelpers": myhelpers}


## todo: persmissionが正しいか確認
@view_config(route_name='page_edit_', renderer='altaircms:templates/page/edit.html', permission='authenticated', 
             decorator=with_fanstatic_jqueries.merge(with_bootstrap))
@view_config(route_name='page_edit', renderer='altaircms:templates/page/edit.html', permission='authenticated', 
             decorator=with_fanstatic_jqueries.merge(with_bootstrap))
def page_edit(context, request):
    """pageの中をwidgetを利用して変更する
    """
    page = request._page = getattr(request, "_page", None) or get_or_404(request.allowable(Page), Page.id==request.matchdict["page_id"])
    try:
        page.valid_layout()
    except ValueError, e:
        FlashMessage.error(str(e), request=request)
        raise HTTPFound(request.route_url("page_update", id=page.id))

    request.page = page
    layout_render = context.get_layout_render(page)
    disposition_select = wf.WidgetDispositionSelectForm()
    user = request.user
    disposition_save = wf.WidgetDispositionSaveForm(page=page.id, owner_id=user.id if user else None)
    disposition_save_default = WidgetDispositionSaveDefaultForm(page=page.id, title=u"%sのデフォルト設定" % page.layout.title)
    ## layoutの選択対象はnone or 同一pagetype?
    layout_qs = request.allowable(Layout).with_transformation(Layout.applicable(page.pagetype_id))
    return {
            'event':page.event,
            'page':page,
            "disposition_select": disposition_select, 
            "disposition_save": disposition_save, 
            "disposition_save_default": disposition_save_default, 
            "layout_candidates": layout_qs, 
            "layout_render":layout_render, 
            "widget_aggregator": get_widget_aggregator_dispatcher(request).dispatch(request, page)
        }

def dispatch_with_rendering_type(rendering_type):
    def _dispatch_with_rendering_type(info, request):
        request._page = getattr(request, "_page", None) or get_or_404(request.allowable(Page), Page.id==request.matchdict["page_id"])
        request._pagetype = getattr(request, "_pagetype", None) or request._page.pagetype
        return request._pagetype.page_rendering_type == rendering_type
    return _dispatch_with_rendering_type

@view_config(route_name="page_edit_", 
             custom_predicates=(dispatch_with_rendering_type("search"),), 
             renderer="altaircms:templates/page/edit_use_search.html", permission="authenticated", 
             decorator=with_fanstatic_jqueries.merge(with_bootstrap))
@view_config(route_name="page_edit", 
             custom_predicates=(dispatch_with_rendering_type("search"),), 
             renderer="altaircms:templates/page/edit_use_search.html", permission="authenticated", 
             decorator=with_fanstatic_jqueries.merge(with_bootstrap))
def page_using_search_edit(context, request):
    page = request._page = getattr(request, "_page", None) or get_or_404(request.allowable(Page), Page.id==request.matchdict["page_id"])
    layout_qs = request.allowable(Layout).with_transformation(Layout.applicable(page.pagetype_id))
    return {"page": page, "layout_candidates": layout_qs}


## widgetの保存 場所移動？
@view_config(match_param="action=save", route_name="disposition", request_method="POST", permission='authenticated')
def disposition_save(context, request):
    form = WidgetDispositionSaveForm(request.POST)
    page = get_or_404(request.allowable(Page), Page.id==request.matchdict["id"])

    if form.validate():
        wdisposition = context.get_disposition_from_page(page, form.data)
        context.add(wdisposition)
        FlashMessage.success(u"widgetのデータが保存されました", request=request)
        return HTTPFound(h.page.to_edit_page(request, page))
    else:
        FlashMessage.error(u"タイトルを入力してください", request=request)
        return HTTPFound(h.page.to_edit_page(request, page))

@view_config(match_param="action=save_default", route_name="disposition", request_method="POST", permission='authenticated')
def disposition_save_default(context, request):
    form = WidgetDispositionSaveDefaultForm(request.POST)
    page = get_or_404(request.allowable(Page), Page.id==request.matchdict["id"])

    if form.validate():
        wdisposition = context.get_disposition_from_page(page, form.data)
        wdisposition.is_public = True
        wdisposition.owner_id = request.user.id
        context.add(wdisposition)
        DBSession.flush()
        layout = get_or_404(request.allowable(Layout), Layout.id==page.layout_id)
        layout.disposition_id = wdisposition.id
        FlashMessage.success(u"現在のレイアウトのデフォルトの設定として保存されました", request=request)
        return HTTPFound(h.page.to_edit_page(request, page))
    else:
        FlashMessage.error(u"タイトルを入力してください", request=request)
        return HTTPFound(h.page.to_edit_page(request, page))

@view_config(match_param="action=load", route_name="disposition", request_method="GET", permission='authenticated')
def disposition_load(context, request):
    page = get_or_404(request.allowable(Page), Page.id==request.matchdict["id"])
    wdisposition = get_or_404(request.allowable(WidgetDisposition), WidgetDisposition.id==request.GET["disposition"])
    loaded_page = context.bind_disposition(page, wdisposition)
    context.add(loaded_page)
    
    FlashMessage.success(u"widgetのデータが読み込まれました", request=request)
    return HTTPFound(h.page.to_edit_page(request, loaded_page))


@view_config(route_name="disposition_list", renderer="altaircms:templates/widget/disposition/list.html", 
             decorator=with_bootstrap, permission='authenticated') #permission
def disposition_list(context, request):
    qs = WidgetDisposition.enable_only_query(request.user)
    ds = request.allowable(WidgetDisposition, qs=qs).options(orm.joinedload(WidgetDisposition.layout))
    return {"ds":ds}

@view_config(route_name="disposition_alter", request_method="POST", permission='authenticated') #permission
def disposition_delete(context, request):
    disposition = get_or_404(request.allowable(WidgetDisposition), WidgetDisposition.id==request.POST["disposition"])
    title = disposition.title
    context.delete_disposition(disposition)
    FlashMessage.success(u"%sを消しました" % title, request=request)
    return HTTPFound(h.widget.to_disposition_list(request))


class PageSetView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='pagesets', renderer="altaircms:templates/pagesets/list.html", decorator=with_bootstrap)
    def pageset_list(self):
        pagesets = self.request.allowable(PageSet)
        return dict(pagesets=pagesets)

    @view_config(route_name='pageset', renderer="altaircms:templates/pagesets/edit.html", decorator=with_bootstrap, request_method="GET")
    def pageset(self):
        pageset_id = self.request.matchdict['pageset_id']
        pageset = get_or_404(self.request.allowable(PageSet), PageSet.id==pageset_id)
        factory = forms.PageSetFormFactory(self.request)
        form = factory(pageset)
        return dict(ps=pageset, form=form, f=factory)

    @view_config(route_name='pageset', renderer="altaircms:templates/pagesets/edit.html", decorator=with_bootstrap, request_method="POST")
    def update_times(self):
        logging.debug('post ')
        pageset_id = self.request.matchdict['pageset_id']
        pageset = get_or_404(self.request.allowable(PageSet), PageSet.id==pageset_id)
        proxy = forms.PageSetFormProxy(pageset)

        factory = forms.PageSetFormFactory(self.request)
        form = factory(pageset)

        if form.validate():
            
            form.populate_obj(proxy)
            FlashMessage.success(u"ページの掲載期間を変更しました", request=self.request)
        else:
            FlashMessage.error(u"期間に誤りがあります", request=self.request)
        return dict(ps=pageset, form=form, f=factory)
