# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from altair.formhelpers import strip_hyphen, strip_spaces
from wtforms import Form
from wtforms import fields
from wtforms import validators as v


class VerifyOrderReuestDataForm(Form):
    order_no = fields.TextField(u"注文番号", filters=[strip_spaces], validators=[v.Required()])
    tel = fields.TextField(u"電話番号", filters=[strip_spaces, strip_hyphen()], validators=[v.Required()])

    def object_validate(self, request, order):
        if order is None or order.shipping_address is None:
            if order is None:
                logger.info("order is Not found. order_no=%s", self.data["order_no"])
            self.errors["order_no"] = [u'注文が見つかりません。受付番号または電話番号が違います。']
            return False
        address = order.shipping_address
        stripper = strip_hyphen()
        if stripper(address.tel_1) != self.data["tel"] and stripper(address.tel_2) != self.data["tel"] :
            self.errors["order_no"] = [u'注文が見つかりません。受付番号または電話番号が違います。']
            return False
        return True
