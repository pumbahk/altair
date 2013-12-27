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
from .domainmodel import ChoosableEvent
from .todict import dict_from_event

@view_config(route_name="event.list", request_method="GET", renderer="json",  permission="sales_counter")
def event_list(context, request):
    operator = context.operator
    logger.info("*event event list operator id=%s", operator.id)
    ev = ChoosableEvent(request, operator)
    now = get_now(request)
    qs = ev.choosable_event_query(now).all()
    return {"events": [dict_from_event(e) for e in qs]}
