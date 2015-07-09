# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
from altaircms.formhelpers import AlignChoiceField
import wtforms.fields as fields
import wtforms.validators as validators
from . import models

class LotsreviewForm(Form):
    _choices = models.LOTSREVIEW_KIND_CHOICES
    kind = fields.SelectField(id="kind", label=u"抽選結果ボタンの種類", choices=_choices)
    external_link = fields.TextField(id="external_link", label=u"外部リンク")
    align = AlignChoiceField(id="align", label="align")

    attributes = fields.HiddenField()
    page_id = fields.IntegerField(id="page_id")

    def validate(self):
        if not super(LotsreviewForm, self).validate():
            return False
        ## align設定追加
        self.attributes.data = dict([("align", self.data["align"])])
        return True
