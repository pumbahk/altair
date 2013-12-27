# -*- coding:utf-8 -*-
from pyramid.view import view_defaults, view_config
import logging
logger = logging.getLogger(__name__)
from altair.now import get_now

class BaseView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


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
        operator = self.context.operator
        if not operator:
            logger.info("*login status operator not found")
            return {"login": False}
        logger.info("*login status operator id=%s", operator.id)
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
    operator = context.operator
    logger.info("*performance list operator id=%s", operator.id)
    ev = ChoosablePerformance(request, operator)
    now = get_now(request)
    qs = ev.choosable_performance_query(now).all()
    return {"performances": [dict_from_performance(e) for e in qs]}

## signed -> qrdata
from .domainmodel import TicketData
@view_config(route_name="qr.ticketdata")
def ticket_data_from_signed_string(context, request)
    signed_string = request.json_body["signed"]
    operator = context.operator
    logger.info("*qr data operator id=%s", operator.id)
    tiket_data = TicketData(request, operator)
    data = ticket_data.ticket_data_from_qrcode(signed_string)
    return data


## token -> [svg] #one
@view_config(route_name="qr.svg.one")
def svg_one_from_token(context, request):
    pass

## order -> [svg] #all
@view_config(route_name="qr.svg.one")
def svg_all_from_order(context, request):
    pass
