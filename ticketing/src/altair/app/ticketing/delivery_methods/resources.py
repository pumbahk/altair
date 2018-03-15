# -*- coding: utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource
from .lookup import lookup_delivery_form_maker

class DeliveryMethodResource(TicketingAdminResource):
    def __init__(self, request):
        super(DeliveryMethodResource, self).__init__(request)
        self.form_maker = lookup_delivery_form_maker(request, self.organization.code)