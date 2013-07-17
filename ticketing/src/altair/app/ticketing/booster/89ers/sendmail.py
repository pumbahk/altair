# -*- coding:utf-8 -*-
from altair.app.ticketing.sej.models import SejOrder

mail_renderer_names = {
    '1': 'mail/89ERS_Completion_EMAIL_NEW_CreditCard.txt',
    '3': 'mail/89ERS_Completion_EMAIL_NEW_SEJ.txt',
    '4': 'mail/89ERS_Completion_EMAIL_NEW_Combined.txt', #xxx:?
}

extra_info_populators = {
    '3': lambda order, value: value.update(dict(sej_order=SejOrder.filter(SejOrder.order_id == order.order_no).first())),
}
