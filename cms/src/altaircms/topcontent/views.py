##
## API views
##
import collections

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPCreated, HTTPOk

from altaircms.lib.apiview import BaseRESTAPI
from altaircms.lib.fanstatic_decorator import with_bootstrap

from . import mappers
from . import forms
from . import models

class TopcontentRESTAPIView(BaseRESTAPI):
    model = models.Topcontent
    form = forms.TopcontentForm
    object_mapper = mappers.TopcontentMapper
    objects_mapper = mappers.TopcontentsMapper

    @view_config(route_name='api_topcontent', request_method='PUT')
    def create(self):
        (created, object, errors) = super(TopcontentRESTAPIView, self).create()
        return HTTPCreated() if created else HTTPBadRequest(errors)

    @view_config(route_name='api_topcontent', request_method='GET', renderer='json')
    @view_config(route_name='api_topcontent_object', request_method='GET', renderer='json')
    def read(self):
        resp = super(TopcontentRESTAPIView, self).read()
        if isinstance(resp, collections.Iterable):
            return self.objects_mapper({'topcontents': resp}).as_dict()
        else:
            return self.object_mapper(resp).as_dict()

    @view_config(route_name='api_topcontent_object', request_method='PUT')
    def update(self):
        status = super(TopcontentRESTAPIView, self).update()
        return HTTPOk() if status else HTTPBadRequest()

    @view_config(route_name='api_topcontent_object', request_method='DELETE')
    def delete(self):
        status = super(TopcontentRESTAPIView, self).delete()
        return HTTPOk() if status else HTTPBadRequest()

@view_config(route_name='topcontent', renderer='altaircms:templates/topcontent/view.mako', permission='topcontent_read',
             decorator=with_bootstrap)
def view(request):
    id_ = request.matchdict['id']
    topcontent = TopcontentRESTAPIView(request, id_).read()
    return dict(
        topcontent=topcontent,
    )

@view_config(route_name="topcontent_delete_confirm", renderer="altaircms:templates/topcontent/delete_confirm.mako", 
             permission="topcontent_delete", request_method="GET", decorator=with_bootstrap)
def delete_confirm(request):
    id_ = request.matchdict['id']
    topcontent = TopcontentRESTAPIView(request, id_).read()
    return dict(
        topcontent=topcontent,
    )

@view_config(route_name="topcontent", permission="topcontent_delete", request_method="POST", decorator=with_bootstrap)
def execute(request):
    id_ = request.matchdict['id']
    TopcontentRESTAPIView(request, id_).get_rest_action(request.POST["_method"])()
    ## fixme: add flash message
    return HTTPFound(location=request.route_path("topcontent_list"))

@view_config(route_name="topcontent_update_confirm", renderer="altaircms:templates/topcontent/update_confirm.mako", 
             permission="topcontent_update", request_method="GET", decorator=with_bootstrap)
def update_confirm(request):
    id_ = request.matchdict['id']
    view  = TopcontentRESTAPIView(request, id_)
    topcontent = view.read()
    form = forms.TopcontentForm(**view.model_object.to_dict())
    return dict(
        topcontent=topcontent, form=form
    )

##
## CMS view
##



@view_config(route_name='topcontent_list', renderer='altaircms:templates/topcontent/list.mako', permission='topcontent_create', request_method="POST", 
             decorator=with_bootstrap)
def _post_list_(request):
    topcontents = TopcontentRESTAPIView(request).read()
    form = forms.TopcontentForm(request.POST)
    if form.validate():
        request.method = "PUT"
        TopcontentRESTAPIView(request).create()
        return HTTPFound(request.route_path("topcontent_list"))

    return dict(
        form=form,
        topcontents=topcontents
    )

@view_config(route_name='topcontent_list', renderer='altaircms:templates/topcontent/list.mako', permission='topcontent_read', request_method="GET", 
             decorator=with_bootstrap)
def _get_list_(request):
    topcontents = TopcontentRESTAPIView(request).read()
    form = forms.TopcontentForm()
    return dict(
        form=form,
        topcontents=topcontents
    )
