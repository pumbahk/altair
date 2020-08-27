# -*- coding:utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource


class ExternalSerialCodeBase(TicketingAdminResource):

    def __init__(self, request):
        super(ExternalSerialCodeBase, self).__init__(request)


class ExternalSerialCodeSettingResource(ExternalSerialCodeBase):
    def __init__(self, request):
        super(ExternalSerialCodeSettingResource, self).__init__(request)
