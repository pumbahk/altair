# coding: utf-8
import collections
from markupsafe import Markup
from pyramid.httpexceptions import HTTPOk, HTTPBadRequest, HTTPCreated, HTTPFound

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.sql.expression import desc

from altaircms.lib.apiview import BaseRESTAPI
from altaircms.models import DBSession
from altaircms.layout.models import Layout
from altaircms.layout.forms import LayoutForm
from altaircms.layout.mappers import LayoutMapper, LayoutsMapper
from altaircms.lib.fanstatic_decorator import with_bootstrap


@view_config(route_name='layout', renderer='altaircms:templates/layout/view.mako', permission='layout_read', 
             decorator=with_bootstrap)
def view(request):
    id_ = request.matchdict.get('layout_id')
    layout = DBSession.query(Layout).get(id_)
    return dict(
        layout=layout
    )


@view_config(route_name='layout_list', renderer='altaircms:templates/layout/list.mako', permission='layout_read', 
             decorator=with_bootstrap)
@view_config(route_name='layout_list', renderer='altaircms:templates/layout/list.mako', permission='layout_create', 
             request_method="POST", decorator=with_bootstrap)
def list(request):
    if request.method == "POST":
        form = LayoutForm(request.POST)
        if form.validate():
            request.method = "PUT"
            LayoutRESTAPIView(request).create()
            return HTTPFound(request.route_path("layout_list"))
    else:
        form = LayoutForm()
    layouts = LayoutRESTAPIView(request).read()

    return dict(
        layouts=layouts,
        form=form,
    )


class LayoutRESTAPIView(BaseRESTAPI):
    model = Layout
    form = LayoutForm
    object_mapper = LayoutMapper
    objects_mapper = LayoutsMapper

    @view_config(route_name='api_layout', request_method='PUT')
    def create(self):
        (created, object, errors) = super(LayoutRESTAPIView, self).create()
        return HTTPCreated() if created else HTTPBadRequest(errors)

    @view_config(route_name='api_layout', request_method='GET', renderer='json')
    @view_config(route_name='api_layout_object', request_method='GET', renderer='json')
    def read(self):
        resp = super(LayoutRESTAPIView, self).read()
        if isinstance(resp, collections.Iterable):
            return self.objects_mapper({'layouts': resp}).as_dict()
        else:
            return self.object_mapper(resp).as_dict()

    @view_config(route_name='api_layout_object', request_method='PUT')
    def update(self):
        status = super(LayoutRESTAPIView, self).update()
        return HTTPOk() if status else HTTPBadRequest()

    @view_config(route_name='api_layout_object', request_method='DELETE')
    def delete(self):
        status = super(LayoutRESTAPIView, self).delete()
        return HTTPOk() if status else HTTPBadRequest()
