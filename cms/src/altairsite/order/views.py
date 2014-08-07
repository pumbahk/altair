from pyramid.httpexceptions import HTTPNotFound
from altairsite.config import usersite_view_config
from altair.mobile.api import is_mobile_request

##workaround.
def pc_access(info, request):
    return not is_mobile_request(request)

@usersite_view_config(route_name='usersite.order', request_method="GET",
                      custom_predicates=(pc_access, ), 
                      renderer='altaircms:templates/usersite/order.html')
def move_order(request):
    if request.organization.short_name != "RT":
        raise HTTPNotFound
    return {}
