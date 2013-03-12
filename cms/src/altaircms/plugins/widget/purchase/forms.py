# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
from altaircms.formhelpers import AlignChoiceField
import wtforms.fields as fields
import wtforms.validators as validators
from . import models

class PurchaseForm(Form):
    _choices = models.PURCHASE_KIND_CHOICES
    kind = fields.SelectField(id="kind", label=u"購入ボタンの種類", choices=_choices)
    external_link = fields.TextField(id="external_link", label=u"外部リンク")
    align = AlignChoiceField(id="align", label="align")

    attributes = fields.HiddenField()
    page_id = fields.IntegerField(id="page_id")

    def validate(self):
        if not super(PurchaseForm, self).validate():
            return False
        ## align設定追加
        style = []
        style.append(self.align.convert_as_style(self.data["align"]))
        style_attributes = u";".join(style)
        self.attributes.data = dict([("style", style_attributes), ("align", self.data["align"])])
        return True
