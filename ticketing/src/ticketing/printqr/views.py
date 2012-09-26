
from pyramid.view import view_config

@view_config(route_name="index", renderer="ticketing.printqr:templates/index.html")
def index_view(request):
    return {}

@view_config(route_name="api.ticket.data", renderer="json")
def ticket_data(context, request):
    return {}
