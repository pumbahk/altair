# -*- coding:utf-8 -*-
from altair.app.ticketing.sej.models import SejOrder

mail_renderer_names = {
    '1': 'mail/bambitious_Completion_EMAIL_NEW_CreditCard.txt',
    '3': 'mail/bambitious_Completion_EMAIL_NEW_SEJ.txt',
    '4': 'mail/bambitious_Completion_EMAIL_NEW_Combined.txt',
}

extra_info_populators = {
    '3': lambda order, value: value.update(dict(sej_order=SejOrder.filter(SejOrder.order_no == order.order_no).first())),
}
