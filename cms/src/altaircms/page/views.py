# coding: utf-8
import colander
import deform
import json

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound

from altaircms.views import BaseRESTAPI
from altaircms.base.views import RegisterViewPredicate
from altaircms.page.forms import PageForm
from altaircms.models import DBSession, Event
from altaircms.page.models import Page

from altaircms.page.mappers import PageMapper, PagesMapper

from altaircms.fanstatic import with_bootstrap
from altaircms.fanstatic import with_fanstatic_jqueries
from altaircms.fanstatic import with_wysiwyg_editor
import altaircms.helpers as h

@view_config(route_name='page', renderer='altaircms:templates/page/list.mako', permission='page_create', request_method="POST", 
             decorator=with_bootstrap)
def create(request):
    form = PageForm(request.POST)
    if form.validate():
        request.method = "PUT"
        PageRESTAPIView(request).create()
        return HTTPFound(request.route_path("page"))
    return dict(
        pages=PageRESTAPIView(request).read(),
        form=form
    )

##
## todo: CRUDのview整理する
##

class WithDefaultConfig(object):
    """view_defaultsがほしい。
    """
    def __init__(self, decorator_, **kwargs):
        self.kwargs = kwargs
        self.decorator = decorator_

    def __call__(self, *args, **kwargs):
        params = kwargs.copy()
        params.update(self.kwargs)
        return self.decorator(*args, **params)

as_delete_view = WithDefaultConfig(view_config, route_name="page_delete", 
                                   permission="page_delete", decorator=with_bootstrap)
as_update_view = WithDefaultConfig(view_config, route_name="page_update", 
                                   permission="page_update", decorator=with_bootstrap)


@as_delete_view(renderer="altaircms:templates/page/delete_confirm.mako", request_method="GET")
def delete_confirm(request):
    id_ = request.matchdict['id']
    page = PageRESTAPIView(request, id_).read()
    return dict(
        page=page,
    )

@as_delete_view(request_method="POST")
def delete(request):
    id_ = request.matchdict['id']
    PageRESTAPIView(request, id_).get_rest_action(request.POST["_method"])()
    ## fixme: add flash message
    return HTTPFound(location=h.page.to_list_page(request))


@as_update_view(renderer="altaircms:templates/page/input.mako",  request_method="GET")
def input(request):
    id_ = request.matchdict['id']
    page = PageRESTAPIView(request, id_).read()
    form = PageForm(**page.to_dict())
    return dict(
        page=page, form=form,
    )

@as_update_view(request_method="POST", renderer="altaircms:templates/page/update_confirm.mako",       
                custom_predicates=[RegisterViewPredicate.confirm])
def update_confirm(request):
    id_ = request.matchdict['id']
    page = PageRESTAPIView(request, id_).read()
    return dict(
        page=page, params=request.POST.items()
    )

@as_update_view(request_method="POST", custom_predicates=[RegisterViewPredicate.execute])
def update(request):
    id_ = request.matchdict['id']
    view = PageRESTAPIView(request, id_)
    view.get_rest_action(request.POST["_method"])()
    ## fixme: add flash message
    return HTTPFound(location=h.page.to_list_page(request))


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

@view_config(route_name='page_edit_', renderer='altaircms:templates/page/edit.mako', permission='authenticated', 
             decorator=with_fanstatic_jqueries.merge(with_bootstrap).merge(with_wysiwyg_editor))
@view_config(route_name='page_edit', renderer='altaircms:templates/page/edit.mako', permission='authenticated', 
             decorator=with_fanstatic_jqueries.merge(with_bootstrap).merge(with_wysiwyg_editor))
def page_edit(request):
    id_ = request.matchdict['page_id']
    page = PageRESTAPIView(request, id_).read()
    if not page:
        return HTTPFound(request.route_path("page"))
    
    layout_render = request.context.get_layout_render(page)
    return {
            'event':page.event,
            'page':page,
            "layout_render":layout_render
        }
