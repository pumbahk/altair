# -*- coding:utf-8 -*-
import json
from altaircms.formhelpers import Form, MaybeIntegerField
from altaircms.formhelpers import AlignChoiceField
import wtforms.fields as fields
import wtforms.validators as validators

class FetchImageForm(Form):
    page = MaybeIntegerField(default=0)
    pk = MaybeIntegerField(default=None, blank_value="null")

class SearchByNameForm(Form):
    search_word = fields.TextField()
    page = MaybeIntegerField(default=0)
    pk = MaybeIntegerField(default=None, blank_value="null")

class SearchByTagForm(Form):
    tags = fields.TextField()
    page = MaybeIntegerField(default=0)
    pk = MaybeIntegerField(default=None, blank_value="null")

class ImageInfoForm(Form):
    href = fields.TextField(id="href", label=u"リンク先")
    width = MaybeIntegerField(id="width", label=u"レンダリングのwidth", validators=[validators.Optional()])
    height = MaybeIntegerField(id="height", label=u"レンダリング時のheight", validators=[validators.Optional()])
    alt = fields.TextField(id="alt", label=u"レンダリング時のalt")
    align = AlignChoiceField(id="align", label="align")
    disable_right_click = fields.BooleanField(label=u"右クリック禁止", id="disable_right_click")

    asset_id = fields.IntegerField(id="asset_id")
    attributes = fields.HiddenField()


    def validate(self):
        if not super(ImageInfoForm, self).validate():
            return False
        ## align設定追加
        data = json.loads(self.attributes.data) if self.attributes.data else {}
        data.update(dict([("data-align", self.data["align"])]))
        self.attributes.data = json.dumps(data)
        return True
