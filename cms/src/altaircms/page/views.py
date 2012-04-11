# coding: utf-8

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound

from altaircms.lib.apiview import BaseRESTAPI
from altaircms.lib.viewhelpers import RegisterViewPredicate
from altaircms.lib.viewhelpers import FlashMessage
from . import forms
from altaircms.page.models import Page
from altaircms.event.models import Event


import altaircms.lib.treat.api as treat
from altaircms.page.mappers import PageMapper, PagesMapper

from altaircms.lib.fanstatic_decorator import with_bootstrap
from altaircms.lib.fanstatic_decorator import with_jquery
from altaircms.lib.fanstatic_decorator import with_fanstatic_jqueries
from altaircms.lib.fanstatic_decorator import with_wysiwyg_editor
import altaircms.helpers as h

##
## todo: CRUDのview整理する
##

@view_defaults(route_name="page_add", decorator=with_bootstrap.merge(with_jquery))
class AddView(object):
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
        form = forms.PageForm(event_id=event.id)
        return {"form":form, "event":event}

    @view_config(request_method="POST", renderer="altaircms:templates/page/add.mako")
    def create_page(self):
        form = forms.PageForm(self.request.POST)
        if form.validate():
            page = treat.get_creator(form, "page", request=self.request).create()
            self.context.add(page)
            ## flash messsage
            FlashMessage.success("page created", request=self.request)
            return HTTPFound(self.request.route_path("event", id=self.event_id))
        else:
            event_id = self.request.matchdict["event_id"]
            event = Event.query.filter(Event.id==event_id).one()
            return {"form":form, "event":event}
        return dict(
            pages=PageRESTAPIView(self.request).read(),
            form=form
            )

@view_defaults(permission="page_create", decorator=with_bootstrap)
class CreateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name="page", renderer='altaircms:templates/page/list.mako', request_method="POST")
    def create(self):
        form = forms.PageForm(self.request.POST)
        if form.validate():
            page = treat.get_creator(form, "page", request=self.request).create()
            self.context.add(page)
            ## flash messsage
            FlashMessage.success("page created", request=self.request)
            return HTTPFound(self.request.route_path("page"))
        return dict(
            pages=PageRESTAPIView(self.request).read(),
            form=form
            )

    @view_config(route_name="page_duplicate", request_method="GET", renderer="altaircms:templates/page/duplicate_confirm.mako")
    def duplicate_confirm(self):
        id_ = self.request.matchdict['id']
        page = PageRESTAPIView(self.request, id_).read()
        return dict(
            page=page,
        )
        
    @view_config(route_name="page_duplicate", request_method="POST")
    def duplicate(self):
        page = self.context.get_page(self.request.matchdict["id"])
        self.context.page_clone(page)
        ## flash messsage
        FlashMessage.success("page duplicated", request=self.request)

        return HTTPFound(self.request.route_path("page"))

@view_defaults(route_name="page_delete", permission="page_delete", decorator=with_bootstrap)
class DeleteView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="altaircms:templates/page/delete_confirm.mako", request_method="GET")
    def delete_confirm(self):
        id_ = self.request.matchdict['id']
        page = PageRESTAPIView(self.request, id_).read()
        return dict(
            page=page,
        )

    @view_config(request_method="POST")
    def delete(self):
        id_ = self.request.matchdict['id']
        PageRESTAPIView(self.request, id_).get_rest_action(self.request.POST["_method"])()

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
class UpdateView(object):
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
        params["tags"] = u', '.join(tag.label for tag in page.public_tags)
        params["private_tags"] = u', '.join([tag.label for tag in page.private_tags])
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
            page = treat.get_updater(form, "page", request=self.request).update(page)
            self.context.add(page)
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
        pages=PageRESTAPIView(request).read(),
        form=form
    )


class PageRESTAPIView(BaseRESTAPI):
    model = Page
    form = forms.PageForm
    object_mapper = PageMapper
    objects_mapper = PagesMapper

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
    id_ = request.matchdict['page_id']
    page = PageRESTAPIView(request, id_).read()
    if not page:
        return HTTPFound(request.route_path("page"))
    
    layout_render = request.context.get_layout_render(page)
    forms = request.context.get_forms(page)
    return {
            'event':page.event,
            'page':page,
            "forms": forms, #forms is dict
            "layout_render":layout_render
        }

## widgetの保存 場所移動？
@view_config(route_name="disposition", request_method="POST", permission='authenticated')
def disposition_save(context, request):
    form = context.get_confirmed_form(request.POST)
    page = context.get_page(request.matchdict["id"])
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
    page = context.get_page(request.matchdict["id"])
    wdisposition = context.get_disposition(request.GET["disposition"])
    page = context.bind_disposition(page, wdisposition)
    context.add(page)
    
    FlashMessage.success(u"widgetのデータが読み込まれました", request=request)
    return HTTPFound(h.page.to_edit_page(request, page))


@view_config(route_name="disposition_list", renderer="altaircms:templates/widget/disposition/list.mako", 
             decorator=with_bootstrap, permission='authenticated') #permission
def disposition_list(context, request):
    ds = context.get_disposition_list(request.user)
    return {"ds":ds}

@view_config(route_name="disposition_alter", request_method="POST", permission='authenticated') #permission
def disposition_delete(context, request):
    disposition = context.get_disposition(request.matchdict["id"])
    title = disposition.title
    context.delete_disposition(disposition)
    FlashMessage.success(u"%sを消しました" % title, request=request)
    return HTTPFound(h.widget.to_disposition_list(request))

