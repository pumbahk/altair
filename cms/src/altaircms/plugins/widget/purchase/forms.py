# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
import wtforms.fields as fields
import wtforms.validators as validators
from . import models

class PurchaseForm(Form):
    _choices = models.PURCHASE_KIND_CHOICES
    kind = fields.SelectField(id="kind", label=u"購入ボタンの種類", choices=_choices)
    external_link = fields.TextField(id="external_link", label=u"外部リンク")
