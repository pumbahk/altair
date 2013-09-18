# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form, MaybeIntegerField
from altaircms.formhelpers import AlignChoiceField
import wtforms.fields as fields
import wtforms.validators as validators

class ImageInfoForm(Form):
    href = fields.TextField(id="href", label=u"リンク先")
    width = MaybeIntegerField(id="width", label=u"レンダリングのwidth", validators=[validators.Optional()])
    height = MaybeIntegerField(id="height", label=u"レンダリング時のheight", validators=[validators.Optional()])
    alt = fields.TextField(id="alt", label=u"レンダリング時のalt")
    align = AlignChoiceField(id="align", label="align")

    asset_id = fields.IntegerField(id="asset_id")
    attributes = fields.HiddenField()
    

    def validate(self):
        if not super(ImageInfoForm, self).validate():
            return False
        ## align設定追加
        self.attributes.data = dict([("data-align", self.data["align"])])
        return True
