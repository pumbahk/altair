# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
import wtforms.fields as fields
import wtforms.validators as validators
from altaircms.formhelpers import AlignChoiceField

class FlashInfoForm(Form):
    width = fields.TextField(id="width", label=u"レンダリングのwidth")
    height = fields.TextField(id="height", label=u"レンダリング時のheight")
    alt = fields.TextField(id="alt", label=u"レンダリング時のalt")
    align = AlignChoiceField(id="align", label="align")

    asset_id = fields.IntegerField(id="asset_id")
    attributes = fields.HiddenField()

    def validate(self):
        if not super(FlashInfoForm, self).validate():
            return False
        ## align設定追加
        self.attributes.data = dict([("align", self.data["align"])])
        return True
