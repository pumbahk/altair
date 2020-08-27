# -*- coding:utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session
from altair.app.ticketing.orders.models import ExternalSerialCodeSetting


class ExternalSerialCodeBase(TicketingAdminResource):

    def __init__(self, request):
        self.session = get_db_session(request, name="slave")
        super(ExternalSerialCodeBase, self).__init__(request)


class ExternalSerialCodeSettingResource(ExternalSerialCodeBase):
    def __init__(self, request):
        super(ExternalSerialCodeSettingResource, self).__init__(request)

    @property
    def settings(self):
        return self.session.query(ExternalSerialCodeSetting) \
            .filter_by(organization_id=self.organization.id) \
            .all()
