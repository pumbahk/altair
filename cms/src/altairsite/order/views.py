from altairsite.config import usersite_view_config

##workaround.
def pc_access(info, request):
    return hasattr(request, "is_mobile") and request.is_mobile == False

@usersite_view_config(route_name='usersite.order', request_method="GET",
                      custom_predicates=(pc_access, ), 
                      renderer='altaircms:templates/usersite/order.html')
def move_order(request):
    return {}
