# coding: utf-8
import logging
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound

from altaircms.lib.viewhelpers import RegisterViewPredicate
from altaircms.lib.viewhelpers import FlashMessage
from . import forms
from altaircms.page.models import Page
from altaircms.page.models import PageSet
from altaircms.event.models import Event


import altaircms.tag.api as tag

from altaircms.lib.fanstatic_decorator import with_bootstrap
from altaircms.lib.fanstatic_decorator import with_jquery
from altaircms.lib.fanstatic_decorator import with_fanstatic_jqueries
from altaircms.lib.fanstatic_decorator import with_wysiwyg_editor
import altaircms.helpers as h


##
## todo: CRUDのview整理する
##

@view_config(route_name="api_page_setup_info", renderer="json")
def api_page_setup_info(request):
    try:
        result = {
            "name": "name", 
            "title": "title", 
            "keywords": "keywords", 
            "description": "description", 
            "parent": 1
            }
        return result
    except Exception, e:
        return {"error": str(e)}

@view_defaults(route_name="page_add", decorator=with_bootstrap.merge(with_jquery))
class PageAddView(object):
    """ eventの中でeventに紐ついたpageの作成
    """
    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.event_id = request.matchdict["event_id"]

    @view_config(request_method="GET", renderer="altaircms:templates/page/add.mako")
    def input_form(self):
        event_id = self.request.matchdict["event_id"]
        event = Event.query.filter(Event.id==event_id).one()
        form = forms.PageForm(event=event)
        setup_form = forms.PageInfoSetupForm()
        return {"form":form, "setup_form": setup_form, "event":event}

    @view_config(request_method="POST", renderer="altaircms:templates/page/add.mako")
    def create_page(self):
        logging.debug('create_page')
        form = forms.PageForm(self.request.POST)
        if form.validate():
            page = self.context.create_page(form)
            ## flash messsage
            FlashMessage.success("page created", request=self.request)
            return HTTPFound(self.request.route_path("event", id=self.event_id))
        else:
            logging.debug("%s" % form.errors)
            event_id = self.request.matchdict["event_id"]
            event = Event.query.filter(Event.id==event_id).one()
            setup_form = forms.PageInfoSetupForm(name=form.data["name"])
            return {"form":form, "event":event, "setup_form": setup_form}

@view_defaults(permission="page_create", decorator=with_bootstrap)
class PageCreateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name="page", renderer='altaircms:templates/page/list.mako', request_method="POST")
    def create(self):
        form = forms.PageForm(self.request.POST)
        if form.validate():
            page = self.context.create_page(form)
            ## flash messsage
            FlashMessage.success("page created", request=self.request)
            return HTTPFound(self.request.route_path("page"))
        else:
            return dict(
                pages=self.context.Page.query,
                form=form
                )

    @view_config(route_name="page_duplicate", request_method="GET", renderer="altaircms:templates/page/duplicate_confirm.mako")
    def duplicate_confirm(self):
        page = self.context.get_page(self.request.matchdict["id"])
        return {"page": page}
        
    @view_config(route_name="page_duplicate", request_method="POST")
    def duplicate(self):
        page = self.context.get_page(self.request.matchdict["id"])
        self.context.clone_page(page)
        ## flash messsage
        FlashMessage.success("page duplicated", request=self.request)

        return HTTPFound(self.request.route_path("page"))

@view_defaults(route_name="page_delete", permission="page_delete", decorator=with_bootstrap)
class PageDeleteView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="altaircms:templates/page/delete_confirm.mako", request_method="GET")
    def delete_confirm(self):
        page = self.context.get_page(self.request.matchdict["id"])
        return {"page": page}

    @view_config(request_method="POST")
    def delete(self):
        page = self.context.get_page( self.request.matchdict['id'])
        self.context.delete_page(page)

        ## flash messsage
        FlashMessage.success("page deleted", request=self.request)

        return HTTPFound(location=h.page.to_list_page(self.request))


class AfterInput(Exception):
    pass

@view_config(route_name="page_update", context=AfterInput, renderer="altaircms:templates/page/input.mako", 
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
        id_ = self.request.matchdict['id']
        page = self.context.get_page(id_)
        params = page.to_dict()
        params["tags"] = tag.tags_to_string(page.public_tags)
        params["private_tags"] = tag.tags_to_string(page.private_tags)
        form = forms.PageUpdateForm(**params)
        return self._input_page(page, form)

    @view_config(request_method="POST", renderer="altaircms:templates/page/update_confirm.mako",       
                    custom_predicates=[RegisterViewPredicate.confirm])
    def update_confirm(self):
        id_ = self.request.matchdict['id']
        form = forms.PageUpdateForm(self.request.POST)
        page = self.context.get_page(id_)
        if form.validate():
            return dict( page=page, params=self.request.POST.items())
        else:
            return self._input_page(page, form)

    @view_config(request_method="POST", custom_predicates=[RegisterViewPredicate.execute])
    def update(self):
        page = self.context.get_page( self.request.matchdict['id'])
        form = forms.PageUpdateForm(self.request.POST)
        if form.validate():
            page = self.context.update_page(page, form)
            ## flash messsage
            FlashMessage.success("page updated", request=self.request)
            return HTTPFound(location=h.page.to_edit_page(self.request, page))
        else:
            return self._input_page(page, form)


@view_config(route_name='page', renderer='altaircms:templates/page/list.mako', 
             permission='page_read', request_method="GET", decorator=with_bootstrap)
def list_(request):
    form = forms.PageForm()
    return dict(
        pages=request.context.Page.query, 
        form=form
    )

@view_config(route_name="page_edit_", request_method="POST")
def to_publish(request):     ## fixme
    page_id = request.matchdict["page_id"]
    page = Page.query.filter(Page.id==page_id).one()
    page.to_published()
    return HTTPFound(request.route_path("page_edit_", page_id=page_id))

## todo: persmissionが正しいか確認
@view_config(route_name='page_edit_', renderer='altaircms:templates/page/edit.mako', permission='authenticated', 
             decorator=with_fanstatic_jqueries.merge(with_bootstrap).merge(with_wysiwyg_editor))
@view_config(route_name='page_edit', renderer='altaircms:templates/page/edit.mako', permission='authenticated', 
             decorator=with_fanstatic_jqueries.merge(with_bootstrap).merge(with_wysiwyg_editor))
def page_edit(request):
    """pageの中をwidgetを利用して変更する
    """
    page = request.context.get_page(request.matchdict["page_id"])
    if not page:
        return HTTPFound(request.route_path("page"))
    
    layout_render = request.context.get_layout_render(page)
    forms = request.context.get_disposition_forms(page)
    return {
            'event':page.event,
            'page':page,
            "forms": forms, #forms is dict
            "layout_render":layout_render
        }

## widgetの保存 場所移動？
@view_config(route_name="disposition", request_method="POST", permission='authenticated')
def disposition_save(context, request):
    form = context.Form(request.POST)
    page = context.Page.query.filter_by(id=request.matchdict["id"]).first()

    if form.validate():
        wdisposition = context.get_disposition_from_page(page, form.data)
        context.add(wdisposition)
        FlashMessage.success(u"widgetのデータが保存されました", request=request)
        return HTTPFound(h.page.to_edit_page(request, page))
    else:
        FlashMessage.error(u"タイトルを入力してください", request=request)
        return HTTPFound(h.page.to_edit_page(request, page))

@view_config(route_name="disposition", request_method="GET", permission='authenticated')
def disposition_load(context, request):
    page = context.Page.query.filter_by(id=request.matchdict["id"]).first()
    wdisposition = context.get_disposition(request.GET["disposition"])
    loaded_page = context.bind_disposition(page, wdisposition)
    context.add(loaded_page)
    
    FlashMessage.success(u"widgetのデータが読み込まれました", request=request)
    return HTTPFound(h.page.to_edit_page(request, loaded_page))


@view_config(route_name="disposition_list", renderer="altaircms:templates/widget/disposition/list.mako", 
             decorator=with_bootstrap, permission='authenticated') #permission
def disposition_list(context, request):
    ds = context.get_disposition_list()
    return {"ds":ds}

@view_config(route_name="disposition_alter", request_method="POST", permission='authenticated') #permission
def disposition_delete(context, request):
    disposition = context.get_disposition(request.matchdict["id"])
    title = disposition.title
    context.delete_disposition(disposition)
    FlashMessage.success(u"%sを消しました" % title, request=request)
    return HTTPFound(h.widget.to_disposition_list(request))


class PageSetView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='pagesets', renderer="altaircms:templates/pagesets/list.mako", decorator=with_bootstrap)
    def pageset_list(self):
        pagesets = PageSet.query.all()
        return dict(pagesets=pagesets)

    @view_config(route_name='pageset', renderer="altaircms:templates/pagesets/edit.mako", decorator=with_bootstrap, request_method="GET")
    def pageset(self):
        pageset_id = self.request.matchdict['pageset_id']
        pageset = PageSet.query.filter_by(id=pageset_id).one()
        factory = forms.PageSetFormFactory(self.request)
        form = factory(pageset)
        return dict(ps=pageset, form=form, f=factory)

    @view_config(route_name='pageset', renderer="altaircms:templates/pagesets/edit.mako", decorator=with_bootstrap, request_method="POST")
    def update_times(self):
        logging.debug('post ')
        pageset_id = self.request.matchdict['pageset_id']
        pageset = PageSet.query.filter_by(id=pageset_id).one()
        proxy = forms.PageSetFormProxy(pageset)

        factory = forms.PageSetFormFactory(self.request)
        form = factory(pageset)

        if form.validate():

            form.populate_obj(proxy)

        return dict(ps=pageset, form=form, f=factory)

