# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from sqlalchemy.sql.expression import and_

from altair.pyramid_dynamic_renderer import lbr_view_config


from altair.app.ticketing.core.models import OrionTicketPhone
from altair.app.ticketing.orderreview.api import send_to_orion
from altair.app.ticketing.orders.models import (Order,
                                                OrderedProduct,
                                                OrderedProductItem,
                                                OrderedProductItemToken)

logger = logging.getLogger(__name__)


class OrionTicketListApiView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='orion.ticket_list',
                     request_method="GET",
                     renderer="json")
    def get(self):
        if not self.context.api_auth():
            logger.error("api authentication fail.")
            return {"success": False, "errcode": "4000", "errmsg": "The authentication is required."}

        phone_number = self.request.params.get('phone_number', None)
        mail = self.request.params.get('mail', None)
        if not phone_number:
            return {"success": False, "errcode": "4000", "errmsg": "phone_number is required."}

        orion_ticket_phones = OrionTicketPhone.query \
            .join(Order, and_(OrionTicketPhone.order_no == Order.order_no)) \
            .filter(OrionTicketPhone.owner_phone_number == phone_number) \
            .filter(OrionTicketPhone.sent == False) \
            .filter(Order.issuing_start_at <= datetime.now()) \
            .filter(Order.canceled_at == None) \
            .filter(Order.refunded_at == None) \
            .filter(Order.paid_at != None)

        fail_order = []

        for orion_ticket_phone in orion_ticket_phones:
            logger.info("sending order: {} to orion...".format(orion_ticket_phone.order_no))
            data_list = self.context.session.query(OrderedProductItemToken) \
                .join(OrderedProductItem) \
                .join(OrderedProduct) \
                .join(Order) \
                .filter(Order.order_no == orion_ticket_phone.order_no)

            for data in data_list:
                response = send_to_orion(self.request, self.context, mail, data)
                if not response or response['result'] != u"OK":
                    fail_order.append(orion_ticket_phone.order_no)
                    logger.info("fail to send order: {0}, token: {1} to orion for phone number: {2}..."
                        .format(orion_ticket_phone.order_no,data.id,phone_number))
                    orion_ticket_phone.sent = False
                else:
                    orion_ticket_phone.sent = True

            orion_ticket_phone.sent_at = datetime.now()
            orion_ticket_phone.update()

        if fail_order:
            success = False
            errcode = "4000"
            errmsg = "fail to send order: {0} to orion for phone number: {1} "\
                .format(','.join(fail_order), phone_number)
        else:
            success = True
            errcode = ""
            errmsg = ""

        return {"success": success, "errcode": errcode, "errmsg": errmsg}
