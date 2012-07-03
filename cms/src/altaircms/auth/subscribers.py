from zope.interface import implementer
from altaircms.interfaces import IAfterResponseEvent
from ..models import DBSession
from . import helpers as h

@implementer(IAfterResponseEvent)
class AfterLogin(object):
    def __init__(self, request, response_data):
        self.request = request
        self.response_data = response_data


def touch_operator_after_login(self): ## self is AfterLogin
    data = self.response_data

    role_names = data.get("roles")
    roles = h.get_roles_from_role_names(role_names)

    operator = h.get_or_create_operator("oauth", data["user_id"], data["screen_name"])
    operator = h.update_operator_with_data(operator, roles, data)
    DBSession.add(operator)
