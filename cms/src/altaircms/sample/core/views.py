from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from altaircms.fanstatic import jqueries_need
from altaircms.fanstatic import wysiwyg_editor_need

@view_config(route_name="ok")
def ok(request):
    from pyramid.response import Response
    return Response("ok")

@view_config(route_name="sample::create_page", renderer="sample/create_page.mak", request_method="GET")
def create_page_form(request):
    form = request.context.get_page_form()
    return {"form" : form}

import deform
@view_config(route_name="sample::create_page", renderer="sample/create_page.mak", request_method="POST")
def create_page(request):
    form = request.context.get_page_form()
    if not "submit" in request.POST:
        return {"form": form}
    try:
        params = form.validate(request.POST.items())
    except deform.ValidationFailure, e:
        return {"form": e}
    # request.context.save_page(params)
    raise HTTPFound(location=request.route_url("ok"))


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
