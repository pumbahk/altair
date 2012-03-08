from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

@view_config(route_name="demo1")
def demo1(request):
    # initialize()
    url = request.route_url("front", page_name="sample_page")
    return HTTPFound(location=url)

# is_initialized = False
# def initialize():
#     global is_initialized
#     if is_initialized:
#         return
#     is_initialized = True
#     from . import initialize
#     initialize.init()
