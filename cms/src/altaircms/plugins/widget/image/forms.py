# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
from altaircms.formhelpers import AlignChoiceField
import wtforms.fields as fields
import wtforms.validators as validators

class ImageInfoForm(Form):
    href = fields.TextField(id="href", label=u"リンク先")
    width = fields.TextField(id="width", label=u"レンダリングのwidth")
    height = fields.TextField(id="height", label=u"レンダリング時のheight")
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

# if __name__ == "__main__":
#     for f in ImageInfoForm():
#         print f()
#     from webob.multidict import MultiDict
#     form = ImageInfoForm(MultiDict(dict(align="center")))
#     form.validate()
#     print form.data

