# -*- coding: utf-8 -*-

from altair.app.ticketing.resources import TicketingAdminResource

class ResaleResource(TicketingAdminResource):
    _base_acl = []
    def __init__(self, request):
        super(ResaleResource, self).__init__(request)