from pyramid.view import view_config

@view_config(route_name='orderpage', request_method="GET",
             renderer='altaircms:templates/usersite/order.html')
def move_order(request):
    return {}