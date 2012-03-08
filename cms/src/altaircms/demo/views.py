from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

@view_config(route_name="demo1")
def demo1(request):
    url = request.route_url("front", page_name="sample_page")
    return HTTPFound(location=url)

@view_config(route_name="demo2")
def demo2(request):
    url = request.route_url("front", page_name="sample_page")
    return HTTPFound(location=url)
