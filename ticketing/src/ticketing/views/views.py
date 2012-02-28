from pyramid.view import view_config

@view_config(route_name='index', renderer='ticketing:templates/index.html')
def index(context, request):
    return {}