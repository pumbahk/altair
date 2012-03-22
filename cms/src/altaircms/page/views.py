# coding: utf-8

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound

from altaircms.views import BaseRESTAPI
from altaircms.base.viewhelpers import RegisterViewPredicate
from altaircms.base.viewhelpers import FlashMessage
from altaircms.page.forms import PageForm
from altaircms.models import Event
from altaircms.page.models import Page

from altaircms.page.mappers import PageMapper, PagesMapper

from altaircms.lib.fanstatic import with_bootstrap
from altaircms.lib.fanstatic import with_fanstatic_jqueries
from altaircms.lib.fanstatic import with_wysiwyg_editor
import altaircms.helpers as h

##
## todo: CRUDのview整理する
##

@view_defaults(permission="page_create", decorator=with_bootstrap)
class CreateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name="page", renderer='altaircms:templates/page/list.mako', request_method="POST")
    def create(self):
        form = PageForm(self.request.POST)
        if form.validate():
            self.request.method = "PUT"
            PageRESTAPIView(self.request).create()

            ## flash messsage
            FlashMessage.success("page created", request=self.request)

            return HTTPFound(self.request.route_path("page"))
        return dict(
            pages=PageRESTAPIView(self.request).read(),
            form=form
            )

    @view_config(route_name="page_add", renderer="altaircms:templates/page/add.mako")
    def add_view(self):
        event_id = self.request.matchdict["event_id"]
        event = Event.query.filter(Event.id==event_id).one()
        form = PageForm()
        return {"form":form, "event":event}

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


@view_defaults(route_name="page_update",permission="page_update", decorator=with_bootstrap)
class UpdateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="altaircms:templates/page/input.mako",  request_method="GET")
    def input(self):
        id_ = self.request.matchdict['id']
        page = PageRESTAPIView(self.request, id_).read()
        form = PageForm(**page.to_dict())
        return dict(
            page=page, form=form,
        )

    @view_config(request_method="POST", renderer="altaircms:templates/page/update_confirm.mako",       
                    custom_predicates=[RegisterViewPredicate.confirm])
    def update_confirm(self):
        id_ = self.request.matchdict['id']
        page = PageRESTAPIView(self.request, id_).read()
        return dict(
            page=page, params=self.request.POST.items()
        )

    @view_config(request_method="POST", custom_predicates=[RegisterViewPredicate.execute])
    def update(self):
        id_ = self.request.matchdict['id']
        view = PageRESTAPIView(self.request, id_)
        view.get_rest_action(self.request.POST["_method"])()

        ## flash messsage
        FlashMessage.success("page updated", request=self.request)

        return HTTPFound(location=h.page.to_list_page(self.request))


@view_config(route_name='page', renderer='altaircms:templates/page/list.mako', 
             permission='page_read', request_method="GET", decorator=with_bootstrap)
def list_(request):
    form = PageForm()
    return dict(
        pages=PageRESTAPIView(request).read(),
        form=form
    )


class PageRESTAPIView(BaseRESTAPI):
    model = Page
    form = PageForm
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

## widgetの保存
@view_config(route_name="disposition", request_method="POST")
def disposition_save(context, request):
    page = context.get_page(request.matchdict["id"])
    wdisposition = context.get_disposition(page)
    context.add(wdisposition)
    
    FlashMessage.success(u"widgetのデータが保存されました", request=request)
    return HTTPFound(h.page.to_edit_page(request, page))

