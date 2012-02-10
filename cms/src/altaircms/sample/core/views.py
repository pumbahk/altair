from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from altaircms.fanstatic import jqueries_need
from altaircms.fanstatic import wysiwyg_editor_need
from deform import ValidationFailure

from . import helpers
from . import mappers

@view_config(route_name="ok")
def ok(request):
    from pyramid.response import Response
    return Response("ok")

@view_config(route_name="sample::create_page", renderer="sample/create_page.mak", request_method="GET")
def create_page_form(request):
    form = request.context.get_page_form()
    return {"form" : form}

@view_config(route_name="sample::create_page", renderer="sample/create_page.mak", request_method="POST")
def create_page(request):
    context = request.context
    form = context.get_page_form()
    if not "submit" in request.POST:
        return {"form": form}
    try:
        params = form.validate(request.POST.items())
        page = context.create_page(params)
        context.add(page, flush=True)
    except ValidationFailure, e:
        return {"form": e}
    return HTTPFound(location=helpers.to_edit_page(request, page.id))

@view_config(route_name="sample::edit_page", renderer="sample/edit_page.mak", request_method="GET")
def edit_page(request):
    page_id = request.matchdict["page_id"]
    page = request.context.get_page(page_id)
    mapper = mappers.UnregisteredPageMapper.as_mapper
    form = request.context.get_page_form(mapper=mapper, appstruct=page)
    return {"page": page, "form": form}

@view_config(route_name="sample::sample", renderer="sample/sample.mak")
def sample(request):
    jqueries_need()
    wysiwyg_editor_need()
    return {}

## todo: deleteit
@view_config(route_name="sample::freetext", renderer="sample/freetext.mak")
def freetext(request):
    wysiwyg_editor_need()
    return {}
