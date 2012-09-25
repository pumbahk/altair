from pyramid.view import view_config

@view_config(route_name="index", renderer="ticketing.printqr:templates/index.html")
def index_view(request):
    return {}
