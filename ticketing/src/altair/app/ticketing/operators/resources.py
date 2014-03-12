# -*- coding: utf-8 -*-

import logging

from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import or_

from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.operators.models import Operator, OperatorRole

logger = logging.getLogger(__name__)


class OperatorAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(type(self), self).__init__(request)

        self.operator_id = None
        self.operator_role_id = None

        if not self.user:
            return

        try:
            self.operator_id = long(self.request.matchdict.get('operator_id'))
        except (TypeError, ValueError):
            pass

        try:
            self.operator_role_id = long(self.request.matchdict.get('operator_role_id'))
        except (TypeError, ValueError):
            pass

        if self.operator_id is not None:
            try:
                self.operator = Operator.query \
                    .filter(Operator.organization_id==self.user.organization_id) \
                    .filter(Operator.id==self.operator_id) \
                    .one()
            except NoResultFound:
                raise HTTPNotFound()
        else:
            self.operator = None

        if self.operator_role_id is not None:
            try:
                self.operator_role = OperatorRole.query \
                    .filter(or_(OperatorRole.organization_id==self.user.organization_id, OperatorRole.organization_id==None)) \
                    .filter(OperatorRole.id==self.operator_role_id) \
                    .one()
            except NoResultFound:
                raise HTTPNotFound()
        else:
            self.operator_role = None

        from altair.app.ticketing.helpers.admin import AdminHelperAdapter
        adapter = AdminHelperAdapter(request)
        for k in dir(adapter):
            if not k.startswith('__'):
                setattr(self, k, getattr(adapter, k))
