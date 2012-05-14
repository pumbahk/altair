from pyramid.view import view_config
from ..front import api as front_api
@view_config(route_name="detail_page_search_input", renderer="altaircms:templates/front/ticketstar/search/detail_search_input.mako")
def detail_page_search_input(request):
    return {}

@view_config(route_name="detail_page_search", renderer="altaircms:templates/front/ticketstar/search/detail_search_result.mako")
def detail_page_search(request):
    return {}

@view_config(route_name="page_search", renderer="altaircms:templates/front/ticketstar/search/search_result.mako")
def page_search(request):
    params = front_api.get_navigation_categories(request)
    return params

