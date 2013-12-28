# -*- coding:utf-8 -*-
from pyramid.view import view_defaults, view_config
import logging
logger = logging.getLogger(__name__)
from altair.now import get_now

class BaseView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

def access_log(prefix, identity):
    if identity:
        logger.info("{prefix} CheckinIdentity.secret=%s, operator.id=%s", identity.secret, identity.operator_id)
    else:
        logger.info("{prefix} CheckinIdentity not found")

## status = {ok, ng}

@view_defaults(route_name="login.status", request_method="GET", renderer="json")
class LoginInfoView(BaseView):
    ## permissionでdispatchできなかったっけ？
    @view_config(permission="everybady")
    def for_guest_user_view(self):
        logger.info("*login status no login user")
        return {"login": False}


    @view_config(permission="sales_counter")
    def for_login_user_view(self):
        access_log("*login status start", self.context.identity)
        operator = self.context.operator
        if not operator:
            return {"login": False}
        return {"login": True,
                "loginuser": {"type": u"login",
                              "id": unicode(operator.id),
                              "name": operator.name},
                "organization": {"id": operator.organization_id}}


## EventSelect
from .domainmodel import ChoosablePerformance
from .todict import dict_from_performance

@view_config(route_name="performance.list", request_method="GET", renderer="json",  permission="sales_counter")
def performance_list(context, request):
    access_log("*performance list", context.identity)
    ev = ChoosablePerformance(request, operator)
    now = get_now(request)
    qs = ev.choosable_performance_query(now).all()
    return {"performances": [dict_from_performance(e) for e in qs]}

# ## signed -> qrdata
# from .domainmodel import TicketData

# @view_config(route_name="qr.ticketdata")
# def ticket_data_from_signed_string(context, request):
#     access_log("*qr.ticketdata", context.identity)
#     try:
#         signed = request.json_body["signed"]
#         signed = re.sub(r"[\x01-\x1F\x7F]", "", signed.encode("utf-8")).replace("\x00", "") .decode("utf-8")
#         tiket_data = TicketData(request, context.operator)
#         data = ticket_data.ticket_data_from_qrcode(signed)
#         return data
#     except KeyError as e:
#         logger.warn(e)
#         raise HTTPBadRequest("signed not found")


# ## token -> [svg] #one
# from .domainmodel import SVGDataListForOne
# from .todict import dict_from_
# @view_config(route_name="qr.svg.one")
# def svg_one_from_token(context, request):
#     access_log("*qr.svg.one", context.identity)
#     vals = request.json_body
#     history_id = vals["exact_id"]
#     order_no = vals["order_no"]
#     ticket, history = get_pair_order_and_ticket_print_history(history_id, order_no)
#     svg_data_list = 


# ## order -> [svg] #all
# @view_config(route_name="qr.svg.one")
# def svg_all_from_order(context, request):
#     pass
